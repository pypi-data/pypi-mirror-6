Less
----

A clean theme for [lilac](https://github.com/hit9/lilac)

less is more, we like minimalist blog design.

Demo
----

http://lilac.hit9.org

Installation
-------------

```
cd /path/to/your/blog
git clone git://github.com/hit9/lilac-theme-less.git less
```

if your blog is git versioning, you should add theme as a submodule:

```
cd /path/to/your/blog
git submodule add git://github.com/hit9/lilac-theme-less.git less
```

Configuration
-------------

You need set `theme` to `"less"` in config.toml:

```
[blog]
theme = "less"
```

`less` needs your github's username:

```
[theme.vars]
github = "your-github-username"
```
