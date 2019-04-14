<html>
<head>
<title>CWG issue browser</title>
</head>
<body>

<h2>CWG issue browser</h2>

<p>
    Issues are scraped from the official lists at
<ul>
%for url, size in urls_and_sizes:
    <li><a href="{{url}}">{{url}}</a> ({{size}})</li>
%end
</ul>
</p>

<ul>
%for issue, status in issues_and_statuses:
    <li><code><a href="/cwg{{issue}}">/cwg{{issue}}</a> ({{status}})</code></li>
%end
</ul>

</body>
</html>
