<% self.seen_css = set() %>
<%def name="css_link(path, media='')" filter="trim">
    % if path not in self.seen_css:
        <link rel="stylesheet" type="text/css" href="${path|h}" media="${media}">
    % endif
    <% self.seen_css.add(path) %>
</%def>
<%def name="css()" filter="trim">
    ${css_link('/static/css/main.css', 'screen')}
</%def>
<%def name="pre()" filter="trim">
    <div class="header">
        <h1><a href="/">Login</a></h1>
    </div>
</%def>
<%def name="post()" filter="trim">
    <div>
        <div class="footer">
            <p>&#169; Copyright 2014 Ume&#229; Universitet &nbsp;</p>
        </div>
    </div>
</%def>
    ##<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN "
##"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
<head>
    ## ${self.css()}
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>Lab 304</title>
</head>
<body>
##  ${pre()}
##        ${comps.dict_to_table(pageargs)}
##        <hr><hr>
${next.body()}
## ${post()}
</body>
</html>
