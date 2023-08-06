# -*- coding: utf-8 -*-
# copyright 2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-nazca postcreate script, executed at instance creation time or when
the cube is added to an existing instance.

You could setup site properties or a workflow here for example.
"""

# Example of site property change
set_property('ui.site-title', "Nazca demo")



# Card
create_entity('Card', content_format=u'text/html', title=u'index',
              content=u"""<div class='row-fluid'>
              <div class='span12'>
              <h1>Welcome on Nazca !</h1><blockquote>
              <p><h3>What is it for ?</h3>
Nazca is a python library aiming to help you to align data. But, what does “align data” mean? For instance, you have a list of cities, described by their name and their country and you would like to find their URI on dbpedia to have more information about them, as the longitude and the latitude. If you have two or three cities, it can be done with bare hands, but it could not if there are hundreds or thousands cities. Nazca provides you all the stuff we need to do it.
</p>
<p><h3>See more</h3>
<ul>
<li><a href='https://www.logilab.org/112574'>Nazca Project</a></li>
<li><a href='http://www.logilab.org/blogentry/115136'>Blog post on Nazca</a></li>
<li><a href='http://www.cubicweb.org'>CubicWeb</a></li>
</ul></p>
</blockquote></div></div>""")
