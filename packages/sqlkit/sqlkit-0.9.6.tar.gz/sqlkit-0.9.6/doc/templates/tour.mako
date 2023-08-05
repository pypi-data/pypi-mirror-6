## coding: utf-8
<%inherit file="layout.mako"/>

<%def name="extrahead()">
    <link rel="stylesheet" href="${pathto('_static/tour.css', 1)}" type="text/css" media="screen" />
    
</%def>

<%def name="prevnextheader()"></%def>


<%def name="sidebar()">

  <div class="sphinxsidebar">
     <div class="sphinxsidebarwrapper">
      <div class="news">

      <h2>Release 0.9.6 is out</h2>
      
      I'm happy to announce that on Jan, 18 2014 I released 
      <a href="${pathto('misc/download', )}#download">version 0.9.6</a> 
      that ports sqlkit to SQLAlchemy rel 0.8+ (<0.9) and adds many minor
      fixes 
						   
      (see <a href="/download/Changelog">changelog</a>). 

	
     </div>
     </div>

   </div>
</%def>

${next.body()}
