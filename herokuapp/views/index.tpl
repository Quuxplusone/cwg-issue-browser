<html>
<head>
<title>CWG issue browser</title>
</head>
<body>

<h2>CWG issue browser</h2>

<p>
    Issues are scraped from the official list at <a href="{{url}}">{{url}}</a>.
%if url_size is not None:
    That page currently weighs in at {{url_size}}.
%end
</p>

%if issue_list is not None:
<ul>
%for issue in issue_list:
    <li><a href="/cwg{{issue}}"><code>/cwg{{issue}}</code></a></li>
%end
</ul>
%else:
<p><a href="/cwg1234"><code>/cwg1234</code></a> for example</p>
%end

</body>
</html>
