"""cubicweb-collaboration application package

Cube for providing facilities for cooperative entity handling
"""
from itertools import chain

from yams.buildobjs import RelationDefinition, RelationType

from cubicweb.predicates import relation_possible
from cubicweb.schema import RQLConstraint, ERQLExpression, RRQLExpression

from cubes.container import ContainerConfiguration


class CollaborationConfiguration(object):
    """Configuration object to make an entity type collaborative.

    Main methods are ``setup_schema``, ``build_hooks``,
    ``build_adapters``, ``setup_ui`` to be respectively in
    post-build/registration callbacks of schema, hooks,
    entities, views respectively.

    Notes about migration:

        *   the method ``rtypes_to_add`` returns collaboration-specific
            relation types to be added.
        *   the method ``etypes_to_sync`` returns entity types to synchronize
            because collaboration modified them (``sync_schema_props_perms``).
    """

    def __init__(self, etype, rtype=None, skiprtypes=(), skipetypes=(),
                 subcontainers=(),
                 clone_rtype=None, clone_skiprtypes=(), clone_skipetypes=(),
                 clone_compulsory_hooks_categories=()):
        if rtype is None:
            rtype = 'in_' + etype.lower()
        self.container_config = ContainerConfiguration(
            etype, rtype, skiprtypes, skipetypes, subcontainers)
        # For convenience.
        self.etype = self.container_config.etype
        self.rtype = self.container_config.rtype
        if clone_rtype is None:
            clone_rtype = 'clone_of_' + etype.lower()
        self.clone_rtype = clone_rtype
        # The sets rtypes/etypes to skip for cloning include respective sets
        # for the container configuration.
        self.clone_skiprtypes = frozenset(clone_skiprtypes + skiprtypes)
        self.clone_skipetypes = frozenset(clone_skipetypes + skipetypes)
        self.clone_compulsory_hooks_categories = clone_compulsory_hooks_categories

    def setup_schema(self, schema,
                     collaborate_permissions=None,
                     container_rtype_permissions=None):
        """ Main setup helper. Inline a modified version of this to customize
        collaboration details to your needs.
        """
        # Setup collaboration container.
        self.container_config.define_container(schema,
                            rtype_permissions=container_rtype_permissions)
        # Setup all collaboration attributes and relations.
        self.setup_clone_rdef(schema)
        self.setup_frozen(schema)
        if collaborate_permissions is None:
            collaborate_permissions = {
                'read': ('managers', 'users'),
                'delete': ('managers', RRQLExpression('O owned_by U')),
                'add': ('managers', RRQLExpression('O owned_by U'))
            }
        self.setup_collaborates_on(schema, perms=collaborate_permissions)

    def rtypes_to_add(self):
        """Return the relation types to be added in migration."""
        return [self.rtype, 'frozen', self.clone_rtype, 'collaborates_on']

    def setup_frozen(self, schema):
        rdef = RelationDefinition(self.etype, 'frozen', 'Boolean',
                                  default=False)
        schema.add_relation_def(rdef)
        # Set constraints on clone rdefs based on 'frozen' attribute.
        for clone_rdef in schema[self.clone_rtype].rdefs.values():
            if clone_rdef.object.type == self.etype:
                frozen_constraint = RQLConstraint('O frozen TRUE')
                if clone_rdef.constraints:
                    clone_rdef.constraints.append(frozen_constraint)
                else:
                    clone_rdef.constraints = [frozen_constraint]

    def setup_clone_rdef(self, schema):
        if not schema.has_relation(self.clone_rtype):
            rtype = RelationType(self.clone_rtype)
            schema.add_relation_type(rtype)
        rdef = RelationDefinition(self.etype, self.clone_rtype, self.etype,
                                  cardinality='?*')
        schema.add_relation_def(rdef)

    def setup_collaborates_on(self, schema, perms):
        rdef = RelationDefinition('CWUser', 'collaborates_on', self.etype,
                                  cardinality='**', __permissions__=perms.copy())
        schema.add_relation_def(rdef)


    def setup_can_read(self, schema, perms):
        rdef = RelationDefinition('CWUser', 'can_read', self.etype,
                                  cardinality='**', __permissions__=perms.copy())
        schema.add_relation_def(rdef)


    def setup_can_write(self, schema, perms):
        rdef = RelationDefinition('CWUser', 'can_write', self.etype,
                                  cardinality='**', __permissions__=perms.copy())
        schema.add_relation_def(rdef)


    def setup_security(self, schema, container_eperms=None,
                       in_container_eperms=None, container_rperms=None,
                       near_container_rperms=None,
                       ignore_rdefs=()):
        """Main security setup helper.
            - container_eperms are the permissions on the container entity (of type etype_name),
            - in_container_eperms are the permissions on the entities contained in the
            container.
            - container_rperms are the permissions on the structural container relations which
            do not point directly to the container itself.
            - near_container_rperms are the permissions on the border container relations, i.e.
            relations between the container entity itself and entities which are in the
            container or out of the container.
            - ignore_rdefs is a tuple of relation definitions, which
            whose permissions have been defined beforehand in the schema, and hence the
            permissions specified in container_rperms / near_container_rperms must not be
            applied to these relation definitions.
        """
        # Permissions for the collaborative entity.
        if container_eperms is None:
            container_eperms = {
            'add': ('managers', 'users'),
            'read': ('managers', ERQLExpression('U can_read X')),
            'update': ('managers', ERQLExpression('U can_write X')),
            'delete': ('managers', ERQLExpression('U can_write X'))
            }
        eschema = schema[self.etype]
        eschema.permissions = container_eperms.copy()
        # can_read/can_write relations.
        perms = {'read': ('managers', 'users'),
                 'delete': ('managers',),
                 'add': ('managers',)}
        self.setup_can_read(schema, perms=perms)
        self.setup_can_write(schema, perms=perms)
        self.setup_container_etype_security(schema, etype_perms=in_container_eperms)
        self.setup_container_rtypes_security(schema, crdef_perms=container_rperms,
                                             near_crdef_perms=near_container_rperms,
                                             ignore_rdefs=ignore_rdefs)

    def setup_container_etype_security(self, schema, etype_perms=None):
        if etype_perms is None:
            read_perms = ERQLExpression(
                'EXISTS(U can_read C, X %s C) OR '
                'NOT EXISTS(X %s C, X owned_by U)' % (self.rtype, self.rtype))
            update_perms = ERQLExpression('U can_write C, X %s C' % self.rtype)
            etype_perms = {
                'read': ('managers', read_perms),
                'add':    ('managers', 'users'), # can't really do it there
                'update': ('managers', update_perms),
                'delete': ('managers', update_perms),
                }
        for etype in self.container_config.structure(schema)[1]:
            eschema = schema[etype]
            eschema.permissions = etype_perms.copy()

    def setup_container_rtypes_security(self, schema, crdef_perms=None, near_crdef_perms=None,
                                        ignore_rdefs=()):
        """Setup permissions on relations."""
        def rdef_perms(update_rql_expr, perms=None):
            """Return rdef permissions using `update_rql_expr` for add/delete
            actions.
            """
            if perms is None:
                update_perm = RRQLExpression(update_rql_expr)
                perms = {'read':   ('managers', 'users'),
                         'add':    ('managers', update_perm),
                         'delete': ('managers', update_perm)}
            return perms
        # Structural relations pointing directly to container root.
        for rschema, role in self.container_config.structural_relations_to_container(schema):
            var = role[0].upper()
            perms = rdef_perms('U can_write %s' % var, near_crdef_perms)
            for rdef in rschema.rdefs.itervalues():
                if rdef not in ignore_rdefs:
                    rdef.permissions = perms.copy()
        # Other structural relations.
        for rschema, role in chain(
                self.container_config.structural_relations_to_parent(schema),
                self.container_config.border_relations(schema)):
            var = role[0].upper()
            perms = rdef_perms('%s %s C, U can_write C' % (var, self.rtype), crdef_perms)
            for rdef in rschema.rdefs.itervalues():
                if rdef not in ignore_rdefs:
                    rdef.permissions = perms.copy()
        # Non-structural relations.
        for rschema in self.container_config.inner_relations(schema):
            perms = rdef_perms('S %s C, U can_write C' % self.rtype, crdef_perms)
            for rdef in rschema.rdefs.itervalues():
                if rdef not in ignore_rdefs:
                    rdef.permissions = perms.copy()

    def build_hooks(self, schema):
        """Return configured container hooks for collaboration."""
        self.setup_on_commit_rtypes_permissions(schema)
        container_hooks = self.container_config.build_container_hooks(schema)
        return container_hooks + (self.build_clone_hook(), )

    def build_clone_hook(self):
        """Build the clone container hook."""
        from cubes.container.hooks import CloneContainer
        from cubicweb.server.hook import Hook, match_rtype
        return type(
            self.etype + 'CloneContainer', (CloneContainer, ),
            {'__select__': Hook.__select__ & match_rtype(self.clone_rtype)})

    def build_adapters(self, schema):
        """Return configured container adapters for collaboration."""
        from cubes.collaboration.entities import (ClonableAdapter,
                                                  CollaborativeITreeAdapter)
        container_protocol = self.container_config.build_container_protocol(schema)
        clone_select = relation_possible(self.clone_rtype,
                                         target_etype=self.etype)
        clone_adapter = type(self.etype + 'CloneAdapter', (ClonableAdapter, ),
                             {'__select__': clone_select,
                              'rtypes_to_skip': self.clone_skiprtypes,
                              'etypes_to_skip': self.clone_skipetypes,
                              'clone_rtype_role': (self.clone_rtype, 'subject'),
                              'compulsory_hooks_categories':
                                self.clone_compulsory_hooks_categories,
                             })
        itree_adapter = type(self.etype + 'ITreeAdapter', (CollaborativeITreeAdapter, ),
                             {'__select__': clone_select,
                              'tree_relation': self.clone_rtype})
        return container_protocol, clone_adapter, itree_adapter

    def setup_on_commit_rtypes_permissions(self, schema):
        """Extend security setup: need to check relations using relation to
        container in their perms on commit.
        """
        from cubicweb.server import ON_COMMIT_ADD_RELATIONS
        for rschema, _ in chain(
                self.container_config.structural_relations_to_container(schema),
                self.container_config.structural_relations_to_parent(schema),
                self.container_config.border_relations(schema)):
            ON_COMMIT_ADD_RELATIONS.add(rschema.type)
        for rschema in self.container_config.inner_relations(schema):
            ON_COMMIT_ADD_RELATIONS.add(rschema.type)

    def setup_ui(self):
        from cubicweb.web.views import uicfg
        _pvs = uicfg.primaryview_section
        _pvs.tag_subject_of(('*', self.rtype, '*'), 'hidden')
        _pvs.tag_object_of(('*', self.rtype, '*'), 'hidden')
        _afs = uicfg.autoform_section
        _afs.tag_subject_of(('*', self.rtype, self.etype), 'main', 'hidden')
        _afs.tag_object_of(('*', self.rtype, self.etype), 'main', 'hidden')
        _afs.tag_subject_of((self.etype, self.clone_rtype, self.etype),
                            'main', 'hidden')
        _afs.tag_object_of((self.etype, self.clone_rtype, self.etype),
                           'main', 'hidden')
