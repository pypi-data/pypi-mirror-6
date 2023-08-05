import os

from django.http import HttpResponse
from django.template import RequestContext, Context
from django.template.loader import get_template
from django.shortcuts import render_to_response
from django.conf import settings

from pygments import highlight
from pygments.styles import get_all_styles
from pygments.lexers import get_all_lexers
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

def pygments(request, template_name="pygments/pygments.html"):
    if request.method == "POST":
        lang = request.POST.get('lang', 'python')
        style = request.POST.get('style', 'default')
        code = request.POST.get('code', '')
        linenos = request.POST.get('linenos', False)
        linenostart = int(request.POST.get('linenostart', 1))
        highlight_lines = request.POST.get('highlight', '').split(',')
        srcattach = request.POST.get('srcattach', False)
        if srcattach == "false":
            srcattach = False
        src_attach_name = request.POST.get('srcattachname', '')
        if linenos == 'true':
            linenos = 'inline'
        else:
            linenos = False
             
        highlighted_code = highlight(code, get_lexer_by_name(lang),
                            HtmlFormatter(
                                cssclass="pygments pygments_%s" % lang,
                                full=False, style=style, noclasses=True,
                                linenos=linenos,
				linenostart=linenostart,
                                hl_lines=highlight_lines),
                            )
        if srcattach:
            source_dir = os.path.join(settings.STATIC_ROOT,
                               getattr(settings,'SOURCE_CODE_FILE_DIR',
                               'static/source/'))
            file_name, source_file = make_unique_file(source_dir,
                                                      src_attach_name)
            source_file.write(code)
            source_file.close() 
            template = get_template('pygments/source_link.html')
            context = Context({"file_name": file_name})
            link_html = template.render(context)
            highlighted_code = link_html + highlighted_code

        return HttpResponse(highlighted_code)
    else:
        styles = list(get_all_styles())
        styles.sort()
        
        langs = [(l[0].strip(), l[1][0].strip()) for l in get_all_lexers()]
        langs.sort()
        
        default_lexers = getattr(settings, 'MCE_DEFAULT_LEXERS', [])
        
	for index, lexer in enumerate(default_lexers):
        	for lang in langs:
                    if lang[0] == lexer:
			langs.remove(lang)
			default_lexers[index] = lang

        langs = default_lexers + langs

        default_style = getattr(settings, 'MCE_DEFAULT_STYLE', None) 
        styles.insert(0, styles.pop(styles.index(default_style)))
        mce_popup_location = getattr(settings, 'MCE_POPUP_LOCATION',
                    'grappelli/tinymce/jscripts/tiny_mce/tiny_mce_popup.js')
        jquery_location = getattr(settings,  'JQUERY_LOCATION' ,
                                         'mezzanine/js/jquery-1.7.1.min.js')
        context = {"styles": styles, "langs": langs,
                   "mce_popup_location": mce_popup_location,
                   "jquery_location": jquery_location}
        return render_to_response(template_name, context,
                                   context_instance=RequestContext(request))

def make_unique_file(source_dir, src_attach_name):
	current_path = os.path.join(source_dir, src_attach_name)
        attempt_count = 1
        modified_name = src_attach_name
        while os.path.exists(current_path):
            modified_name = ('_%s' % attempt_count).join(
                                 os.path.splitext(src_attach_name))
            attempt_count += 1
            current_path = os.path.join(source_dir, modified_name)
        return modified_name, open(current_path, "w")
