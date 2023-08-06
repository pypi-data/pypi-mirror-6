FROM fedora

ADD . /srv/{{ basename }}{% if venv %}/{{ basename }}{% endif %}

{% if venv %}
WORKDIR /srv
{% endif %}
{{ setup_command }}
EXPOSE 8000
{% if venv %}
CMD source /srv/{{ basename }}/bin/activate && \
 /srv/{{ basename }}/{{ basename }}/manage.py runserver 0.0.0.0:8000
{% else %}
CMD /srv/{{ basename }}/manage.py runserver 0.0.0.0:8000
{% endif %}
