<head prefix="og: http://ogp.me/ns#
              fb: http://ogp.me/ns/fb#
% for prefix, uri in prefixes.items():
              ${prefix}: ${uri}
% endfor
             ">
% for property, value in properties.items():
%     if isinstance(value, list):
%         for element in value:
%             for subproperty, subvalue in element.items():
  <meta property="${property}:${subproperty}" content="${subvalue}"/>
%             endfor
%         endfor
%     else:
  <meta property="${property}" content="${value}"/>
%     endif
% endfor
</head>
## TODO redirect URI
