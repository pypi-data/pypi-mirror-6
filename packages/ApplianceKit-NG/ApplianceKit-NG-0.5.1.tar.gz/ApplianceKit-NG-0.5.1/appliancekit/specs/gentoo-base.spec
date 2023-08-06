{% extends "base.spec" %}
{% block bootstrap %}
	{{ super() }}
	{"operation": "runcmd", "chroot": false, "command": ["wget", "http://isomaster.tortois.es/cache/gentoo-bootstrap-{{ distribution }}.tar.bz2", "-O", "$chroot/ak-gentoo-bundle.tar.bz2"]},
	{"operation": "runcmd", "chroot": false, "command": ["tar", "-C", "$chroot", "-jxf", "$chroot/ak-gentoo-bundle.tar.bz2"]},
{% endblock %}
{% block packages %}
	{% for package in packages %}
		{"operation": "runcmd", "chroot": true, "command": ["emerge", "{{ package }}"]},
	{% endfor %}
{% endblock %}
{% block configure %}
	{{ super() }}
	{"operation": "render_template", "template": "gentoo/hostname.tmpl", "target": "/etc/conf.d/hostname"},
	{"operation": "render_template", "template": "gentoo/net.tmpl", "target": "/etc/conf.d/net"},
	{"operation": "runcmd", "chroot": true, "command": ["ln", "-sf", "/etc/init.d/net.lo", "/etc/init.d/net.eth0"]},
	{"operation": "runcmd", "chroot": true, "command": ["rc-update", "add", "net.eth0", "default"]},
	{"operation": "render_template", "template": "gentoo/locale-gen.tmpl", "target": "/etc/locale.gen"},
	{"operation": "runcmd", "chroot": true, "command": ["locale-gen"]},
{% endblock %}
