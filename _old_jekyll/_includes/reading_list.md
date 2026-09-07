<h2 id="reading-list" style="margin: 2px 0px -15px;">Reading List</h2>

<div class="publications">

{% for category in site.data.reading_list.categories %}

<h3 style="margin: 25px 0px 5px;">{{ category.name }}</h3>

{% for subcategory in category.subcategories %}

<h4 style="margin: 10px 10px 5px;">{{ subcategory.name }}</h4>

<ol class="bibliography">
{% for paper in subcategory.papers %}
<li>
<div class="pub-row">
  <div class="col-sm-9" style="position: relative;padding-right: 15px;padding-left: 20px;">
      <div class="title"><a href="{{ paper.link }}">{{ paper.title }}</a></div>
      <div class="author">{{ paper.authors }}</div>
      <div class="periodical"><em>{{ paper.venue }}</em></div>
    <div class="links">
      {% if paper.link %}
      <a href="{{ paper.link }}" class="btn btn-sm z-depth-0" role="button" target="_blank" style="font-size:12px;">Link</a>
      {% endif %}
      {% if paper.code %}
      <a href="{{ paper.code }}" class="btn btn-sm z-depth-0" role="button" target="_blank" style="font-size:12px;">Code</a>
      {% endif %}
      {% if paper.notes %}
      <strong><i style="color:#e74d3c">{{ paper.notes }}</i></strong>
      {% endif %}
    </div>
  </div>
</div>
</li>
<br>
{% endfor %}
</ol>

{% endfor %}
{% endfor %}

</div>
