# -*- encoding: utf-8 -*-
"""
This module contains a tag for rendering trees from sequences.

For this, a method for recursion is given, as well as for defining start and end
markers. A full example of the syntax of this template tag is the following:

  {% tree item_seq %}
  <ul>                             {# indentation section #}
  {% for item in tree %}           {# item start #}
  <li>{{ item.description }}
      {% subtree item.sub_seq %}
  </li>
  {% endfor %}                     {# item end #}
  </ul>                            {# outdentation section #}
  {% endtree %}

The syntax defined here thus has two special tags and splits into three
sections. The sections are:

1. The tree indentation section
2. The tree item section
3. The tree outdentation section

Start a tree by enclosing the whole of the tree code with a `tree`/`endtree` tag
pair. The `tree` tag needs to receive one argument, a sequence of items. This
sequence will be available inside the tree as a variable named `tree`. The
renaming is necessary so we can map the sequence in subtrees to the same name.

The three sections are separated by a `for`-loop looping over the items.

In the tree indentation section, place everything that belongs to the 'head' of
a tree, like the start tags of a list or a table. 

In the item section, place everything that renders the item, as well as the
special recursive tag that renders the subtree. The `subtree` tag simply takes

Finally in the outdentation section, place everything that closes the tree, like
the closing of the list or table tags and any footer material for the tree.


Nested trees are not supported at the moment (i.e. placing a `tree` section
inside of another `tree` section).
"""

import datetime

from django import template

register = template.Library()


class TreeNode(template.Node):
    
    def __init__(self, nodelist, tree_seq_var):
        self.nodelist = nodelist
        self.tree_seq_var = tree_seq_var
        
    def render(self, context, tree_seq=None):
        
        context.push()
        
        try:
            tree_seq = tree_seq or self.tree_seq_var.resolve(context)
            context['tree'] = tree_seq
            context['treetag'] = self
        except template.base.VariableDoesNotExist:
            pass
        
        output = self.nodelist.render(context)
        
        context.pop()
        return output


class SubTreeNode(template.Node):
    
    def __init__(self, tree_seq_var):

        self.tree_seq_var = template.Variable(tree_seq_var)
        
    def render(self, context):
        
        parent_tree = context.get('treetag')
        if not parent_tree:
            return ''
        try:
            subtree_seq = self.tree_seq_var.resolve(context)
        except template.base.VariableDoesNotExist:
            return ''
            
        if not subtree_seq:
            return ''
        else:
            return parent_tree.render(context, tree_seq=subtree_seq)


@register.tag(name="tree")
def do_tree(parser, token):
    try:
        tag_name, tree_seq_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "{} tag requires a single argument: the name of the sequence of items".format(
                token.contents.split()[0]
            )
        )
        
    if tree_seq_name[0] in ('"', "'") or tree_seq_name[-1] in ('"', "'"):
        raise template.TemplateSyntaxError(
            "{} tag argument must be a variable name".format(
                tag_name
            )
        )

    nodelist = parser.parse(('endtree',))
    parser.delete_first_token()
    tree_seq_var = template.Variable(tree_seq_name)

    return TreeNode(nodelist, tree_seq_var)


@register.tag(name="subtree")
def do_subtree(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, subtree_seq_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "{} tag requires a single argument: the name of the sequence of items".format(
                token.contents.split()[0]
            )
        )
    if subtree_seq_name[0] in ('"', "'") or subtree_seq_name[-1] in ('"', "'"):
        raise template.TemplateSyntaxError(
            "{} tag argument must be a variable name".format(
                tag_name
            )
        )
        
    return SubTreeNode(subtree_seq_name)



