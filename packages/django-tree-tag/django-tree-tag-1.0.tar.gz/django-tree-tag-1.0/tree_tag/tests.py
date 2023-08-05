"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.template import Template, Context

class TreeRenderTest(TestCase):

    def test_canonical_tree(self):
        """Render the template in the documentation with a tree input."""
    
        template = """
        {% load treetag %}{% spaceless %}

  {% tree item_seq %}
  <ul>                             {# indentation section #}
  {% for item in tree %}           {# item start #}
  <li>
    {{ item.0 }}
    {% subtree item.1 %}
  </li>
  {% endfor %}                     {# item end #}
  </ul>                            {# outdentation section #}
  {% endtree %}
  
      {% endspaceless %}
        """
    
        t = Template(template)
        c = Context({
            'item_seq':
            [
            (1, None),
            (2, None),
            (3, [
                ('3.1', [
                    ('3.1.1', None),
                    ('3.1.2', None),
                ]),
                ('3.2', [
                    ('3.2.1', None),
                    ('3.2.2', None),
                ]),
                ]),
            (4, None),
            ],
        })
        
        # uh, I made that manually!
        expected = u'\n        <ul><li>\n    1\n    \n  </li><li>\n    2\n    \n  </li><li>\n    3\n    \n  <ul><li>\n    3.1\n    \n  <ul><li>\n    3.1.1\n    \n  </li><li>\n    3.1.2\n    \n  </li></ul></li><li>\n    3.2\n    \n  <ul><li>\n    3.2.1\n    \n  </li><li>\n    3.2.2\n    \n  </li></ul></li></ul></li><li>\n    4\n    \n  </li></ul>\n        '
        
        self.assertEqual(expected, t.render(c))
        
    def test_canonical_flat(self):
        """Render the template in the documentation with a flat input."""
    
        template = """
        {% load treetag %}{% spaceless %}

  {% tree item_seq %}
  <ul>                             {# indentation section #}
  {% for item in tree %}           {# item start #}
  <li>{{ item.0 }}{% subtree item.1 %}</li>
  {% endfor %}                     {# item end #}
  </ul>                            {# outdentation section #}
  {% endtree %}
  
      {% endspaceless %}
        """
    
        t = Template(template)
        c = Context({
            'item_seq':
            [
            (1, None),
            (2, None),
            (3, None),
            (4, None),
            ],
        })
        
        expected = u'\n        <ul><li>1</li><li>2</li><li>3</li><li>4</li></ul>\n        '
        
        self.assertEqual(expected, t.render(c))

    
    
    def test_canonical_2(self):
        """Render the in the documentation with several inputs."""
    
        template = """
        {% load treetag %}{% spaceless %}

  {% tree item_seq %}
  <ul>                             {# indentation section #}
  {% for item in tree %}           {# item start #}
  <li>
    {{ item.0 }}
    {% subtree item.1 %}
  </li>
  {% endfor %}                     {# item end #}
  </ul>                            {# outdentation section #}
  {% endtree %}
  
      {% endspaceless %}
        """
    
        t = Template(template)
        c = Context({
            'item_seq':
            [
            (1, None),
            (2, None),
            (3, [
                ('3.1', [
                    ('3.1.1', None),
                    ('3.1.2', None),
                ]),
                ('3.2', [
                    ('3.2.1', None),
                    ('3.2.2', None),
                ]),
                ]),
            (4, None),
            ],
        })
        
        print t.render(c)
        print repr(t.render(c))
    
