########################################################################
# amara/xupdate/commands.py
"""
XUpdate request processing
"""

from amara import tree
from amara.lib.xmlstring import splitqname
from amara.xpath import context
from amara.xupdate import XUpdateError, xupdate_primitive

__all__ = [
    'insert_before_command', 'insert_after_command', 'append_command',
    'update_command', 'rename_command', 'remove_command',
    'variable_command', 'if_command'
    ]


# XQuery Update to XUpdate mapping
# upd:insertBefore           xupdate:insert-before
# upd:insertAfter            xupdate:insert-after
# upd:insertInto             xupdate:append
# upd:insertIntoAsFirst      xupdate:append (@child=1)
# upd:insertIntoAsLast       xupdate:append
# upd:insertAttributes       xupdate:append (content=xupdate:attribute)
# upd:delete                 xupdate:remove
# upd:replaceNode            <pending>
# upd:replaceValue           xupdate:update (@select=[attr,text,comment,pi])
# upd:replaceElementContent  xupdate:update (@select=[element])
# upd:rename                 xupdate:rename


class modifications_list(xupdate_primitive):

    def apply_updates(self, document):
        ctx = context(document)
        for command in self:
            command.instantiate(ctx)
        return document

    def __repr__(self):
        return '<modifications: %s>' % list.__repr__(self)


class xupdate_command(xupdate_primitive):
    pass


class append_command(xupdate_command):
    pipeline = 1
    __slots__ = ('namespaces', 'select', 'child')
    def __init__(self, namespaces, select, child=None):
        # save in-scope namespaces for XPath
        self.namespaces = namespaces
        # required `select` attribute
        self.select = select
        # optional `child` attribute
        self.child = child
        return

    def __repr__(self):
        return '<append: %s>' % xupdate_command.__repr__(self)

    def instantiate(self, context):
        context.namespaces = self.namespaces
        targets = self.select.evaluate_as_nodeset(context)
        if not targets:
            raise XUpdateError(XUpdateError.INVALID_SELECT)
        for target in targets:
            context.push_tree_writer(target.xml_base)
            for primitive in self:
                primitive.instantiate(context)
            writer = context.pop_writer()
            tr = writer.get_result()
            if self.child:
                focus = context.node, context.position, context.size
                try:
                    context.node = target
                    context.position = 1
                    size = context.size = len(target.xml_children)
                    position = int(self.child.evaluate_as_number(context))
                finally:
                    context.node, context.position, context.size = focus
                if position < size:
                    refnode = target.xml_children[position]
                else:
                    refnode = None
            else:
                refnode = None
            while tr.xml_first_child:
                if refnode is not None:
                    offset = target.xml_index(refnode)
                    target.xml_insert(offset, tr.xml_first_child)
                else:
                    target.xml_append(tr.xml_first_child)
        return


class rename_command(xupdate_command):
    pipeline = 1
    __slots__ = ('namespaces', 'select',)
    def __init__(self, namespaces, select):
        # save in-scope namespaces for XPath
        self.namespaces = namespaces
        # required `select` attribute
        self.select = select

    def __repr__(self):
        return '<rename: %s>' % xupdate_command.__repr__(self)

    def instantiate(self, context):
        context.push_string_writer(errors=False)
        for primitive in self:
            primitive.instantiate(context)
        writer = context.pop_writer()
        name = writer.get_result()
        prefix, local = splitqname(name)
        if prefix:
            namespace = self.namespaces[prefix]
        else:
            namespace = None

        context.namespaces = self.namespaces
        targets = self.select.evaluate_as_nodeset(context)
        if not targets:
            raise XUpdateError(XUpdateError.INVALID_SELECT)
        for target in targets:
            parent = target.xml_parent
            if target.xml_type == tree.attribute.xml_type:
                parent.xml_attributes[namespace, name] = target.xml_value
            elif target.xml_type == tree.processing_instruction.xml_type:
                pi = tree.processing_instruction(name, target.xml_data)
                parent.xml_replace-child(pi, target)
            elif target.xml_type == tree.element.xml_type:
                #FIXME: Use regular constructor. No more DOM factory
                element = tree.element(namespace, name)
                # Copy any existing attributes to the newly created element
                if target.xml_attributes:
                    for (ns, qname), value in target.xml_attributes.iteritems():
                        element.xml_attributes[ns, qname] = value
                # Now copy any children as well
                while target.xml_first_child:
                    element.xml_append(target.xml_first_child)
                parent.xml_replace(target, element)
        return


class insert_before_command(xupdate_command):
    pipeline = 2
    __slots__ = ('namespaces', 'select',)
    def __init__(self, namespaces, select):
        # save in-scope namespaces for XPath
        self.namespaces = namespaces
        # required `select` attribute
        self.select = select
        return

    def __repr__(self):
        return '<insert-before: %s>' % xupdate_command.__repr__(self)

    def instantiate(self, context):
        context.namespaces = self.namespaces
        for target in self.select.evaluate_as_nodeset(context):
            context.push_tree_writer(target.xml_base)
            for primitive in self:
                primitive.instantiate(context)
            writer = context.pop_writer()
            tr = writer.get_result()
            parent = target.xml_parent
            while tr.xml_first_child:
                offset = parent.xml_index(target)
                parent.xml_insert(offset, tr.xml_first_child)
        return


class insert_after_command(xupdate_command):
    pipeline = 2
    __slots__ = ('namespaces', 'select',)
    def __init__(self, namespaces, select):
        # save in-scope namespaces for XPath
        self.namespaces = namespaces
        # required `select` attribute
        self.select = select
        return

    def __repr__(self):
        return '<insert-after: %s>' % xupdate_command.__repr__(self)

    def instantiate(self, context):
        context.namespaces = self.namespaces
        for target in self.select.evaluate_as_nodeset(context):
            context.push_tree_writer(target.xml_base)
            for primitive in self:
                primitive.instantiate(context)
            writer = context.pop_writer()
            tree = writer.get_result()
            parent = target.xml_parent
            target = target.xml_following_sibling
            while tree.xml_first_child:
                if target is not None:
                    offset = parent.xml_index(target)
                    parent.xml_insert(offset, tree.xml_first_child)
                else:
                    parent.xml_append(tree.xml_first_child)
        return


class update_command(xupdate_command):
    pipeline = 3
    __slots__ = ('namespaces', 'select',)
    def __init__(self, namespaces, select):
        # save in-scope namespaces for XPath
        self.namespaces = namespaces
        # required `select` attribute
        self.select = select
        return

    def __repr__(self):
        return '<update: %s>' % xupdate_command.__repr__(self)

    def instantiate(self, context):
        context.namespaces = self.namespaces
        targets = self.select.evaluate_as_nodeset(context)
        if not targets:
            raise XUpdateError(XUpdateError.INVALID_SELECT)
        for target in targets:
            if target.xml_type == tree.element.xml_type:
                context.push_tree_writer(target.xml_base)
                for primitive in self:
                    primitive.instantiate(context)
                writer = context.pop_writer()
                tr = writer.get_result()
                while target.xml_first_child:
                    target.xml_remove(target.xml_first_child)
                while tr.xml_first_child:
                    target.xml_append(tr.xml_first_child)
            elif target.xml_type in (tree.attribute.xml_type,
                                     tree.text.xml_type,
                                     tree.comment.xml_type,
                                     tree.processing_instruction.xml_type):
                context.push_string_writer(errors=False)
                for primitive in self:
                    primitive.instantiate(context)
                writer = context.pop_writer()
                value = writer.get_result()
                if not value and target.xml_type == tree.text.xml_type:
                    target.xml_parent.xml_remove(target)
                else:
                    target.xml_value = value
        return


class remove_command(xupdate_command):
    pipeline = 4
    __slots__ = ('namespaces', 'select',)
    def __init__(self, namespaces, select):
        # save in-scope namespaces for XPath
        self.namespaces = namespaces
        # required `select` attribute
        self.select = select
        return

    def __repr__(self):
        return '<remove select=%s>' % (self.select,)

    def instantiate(self, context):
        context.namespaces = self.namespaces
        for target in self.select.evaluate_as_nodeset(context):
            parent = target.xml_parent
            if parent:
                if target.xml_type == tree.attribute.xml_type:
                    del parent.xml_attributes[target]
                else:
                    parent.xml_remove(target)
        return


class variable_command(xupdate_command):
    __slots__ = ('namespaces', 'name', 'select')
    def __init__(self, namespaces, name, select=None):
        # save in-scope namespaces for XPath
        self.namespaces = namespaces
        # require `name` attribute
        self.name = name
        # optional `select` attribute
        self.select = select
        return

    def __repr__(self):
        return '<variable: %s>' % xupdate_command.__repr__(self)

    def instantiate(self, context):
        if self.select:
            context.namespaces = self.namespaces
            value = self.select.evaluate(context)
        else:
            context.push_string_writer(errors=False)
            for primitive in self:
                primitive.instantiate(context)
            writer = context.pop_writer()
            value = writer.get_result()
        context.variables[self.name] = value
        return


class if_command(xupdate_command):
    __slots__ = ('namespaces', 'test',)
    def __init__(self, namespaces, test):
        # save in-scope namespaces for XPath
        self.namespaces = namespaces
        # require `test` attribute
        self.test = test
        return

    def __repr__(self):
        return '<if: %s>' % xupdate_command.__repr__(self)
