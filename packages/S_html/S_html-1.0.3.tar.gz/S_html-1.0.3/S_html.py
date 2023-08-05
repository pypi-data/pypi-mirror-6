""" The Class Pi_html provides a simple and easy to use framework to create HTML documents"""
import urllib.parse
class Pi_html:
  def __init__(self, title):
    self.docType = "<!doctype html />"
    self.docLang = "en"
    self.charSet = "iso-8859-1"
    self.favIcon = "img/favicon.ico"
    self.title = title
    self.styleSheet = "<link rel='stylesheet' type='text/css' href='../css/pi_html.css' />"
    self.script = "<script type='text/javascript' src='../js/lib/modernizr.custom.js'></script> \n"
    self.extrasHead = ""
    self.navMenus = ""
    self.h1 = "S-HTML Class Demo"
    self.pageTabs = ""
    self.bodyContent = ""
    self.footer = "<p>This page was created using the S-HTML Framework</p>"
    self.extrasBody = ""
    self.browser = ""
    navMenus = [["Home", "home"],
                ["Reports", [["Tables", [["Table1", "table1"],
                                         ["Table2", "table2"]]],
                             ["Charts", [["Chart1", "chart1"],
                                         ["Chart2", "chart2"]]]]],
                ["Contact", "contact"],
                ["Help", "help"],
                ["About", "about"]]
    self.add_navMenus(navMenus)

  def add_styleSheet(self, css_file):
    self.styleSheet += "\n" + " " * 4 + "<link rel='stylesheet' href='css/{}' />".format(css_file)

  def add_script(self, js_file):
    self.script += "\n" + " " * 4 +"<script type='text/javascript' src='../js/$js_file'></script>"

  def add_extraHead(self, head_extra):
    self.extrasHead += "\n" + " " * 4 + head_extra

  def add_extraBody(self, body_extra):
    self.extrasBody += "\n" + " " * 4 + body_extra

  def add_bodyContent(self, content):
    self.bodyContent += " " * 4 + content + "\n"

  def add_navMenus(self, menus_array):
    self.navMenus = "<nav>\n"
    self.ul_li(menus_array, 4)
    self.navMenus += "      </nav>"

  def ul_li(self, list_array, indent_level):
    self.navMenus += "  " * indent_level + "<ul>\n"
    for each_item in list_array:
      if isinstance(each_item[1], list):
        self.navMenus += "  " * (indent_level + 1) + "<li><a href='#' title='{title}'>{title}</a>\n".format(title = each_item[0])
        self.ul_li(each_item[1], indent_level + 1)
      else:
        self.navMenus += "  " * (indent_level + 1) + "<li><a href='{link}' title='{title}'>{title}</a></li>\n".format(title = each_item[0], link = each_item[1])
    self.navMenus += "  " * indent_level + "</ul></li>\n"

  def add_pageTabs(self, tabs_array):
    self.pageTabs = "\n" + " " * 6 + "<table id='pageTabs'><thead><tr>"
    for each_tab in tabs_array:
      if each_tab[2] == True:
        active = "id='activeTab'"
      else:
        active = ""
      self.pageTabs += "<th {active}><a href='{link}' title='{title}'>{title}</a></th>".format(active = active, title = each_tab[0], link = each_tab[1])
    self.pageTabs += "</tr></thead></table>"

  def tag(self, tag, attributes, content):
    result = "\n" + " " * 4 + "<{a} {b}>{c}</{a}>".format(a = tag, b = attributes, c = content)
    return result

  def img(self, source, attributes):
    result = "\n" + " " * 4 + "<img src='{a}' {b} />".format(a = parameter, b = attributes)
    return result

  def showHTML(self):
    html_code = """{docType}
<html lang='{docLang}'>
  <head>
    <meta charset='{charSet}' />
    <title>{title}</title>
    <link rel='icon' href='{favIcon}' type='image/ico' />
    <link rel='shortcut icon' href='{favIcon}' type='image/x-icon' />
    {styleSheet}
    {script}
    {extrasHead}
  </head>
  <body>
    <header>
      {navMenus}
      <h1>{h1}</h1>
      {pageTabs}
    </header>
    <section id='bodyContent'>
    {bodyContent}
    </section>
    <footer>
      {footer}
    </footer>
    {extrasBody}
  </body>
</html>""".format(docType = self.docType, docLang = self.docLang, charSet = self.charSet,
                  title = self.title, favIcon = self.favIcon, styleSheet = self.styleSheet,
                  script = self.script, extrasHead = self.extrasHead, navMenus = self.navMenus,
                  h1 = self.h1, pageTabs = self.pageTabs, bodyContent = self.bodyContent,
                  footer = self.footer, extrasBody = self.extrasBody)
    return html_code

""" The Class Fielset complements the Pi_HTML class to manage fieldsets"""
class Fieldset:
  def __init__(self, legend, content):
    self.legend = legend
    self.content = content

  def add_item(self, content):
    self.content += "\n" + " " * 6 + content

  def showHTML(self):
    result = """<fieldset><legend>{legend}:</legend>
      {content}
    </fieldset>""".format(legend = self.legend, content = self.content)
    return result

""" The Class Table complements the Pi_HTML class to manage tables"""
class Table:
  def __init__(self, summary, tableClass):
    self.summary = summary
    self.tableClass = tableClass
    self.details = True
    self.headers = ""
    self.footer = ""
    self.rowContent = ""
    self.columns = 0
    self.rows = 0

  def add_header(self, headers):
    self.headers += "\n" + " " * 10 + "<tr>"
    for each_th in headers:
      self.headers += "\n" + " " * 12 + "<th>" + each_th + "</th>"
      self.columns = self.columns + 1
    self.headers += "\n" + " " * 10 + "</tr>"

  def add_row(self, rowContent):
    self.rowContent += "\n" + " " * 10 + "<tr>"
    for each_td in rowContent:
      self.rowContent += "\n" + " " * 12 + "<td>" + each_td + "</td>"
      self.rows = self.rows + 1
    self.rowContent += "\n" + " " * 10 + "</tr>"

  def add_footer(self, footer):
    self.footer += "\n" + " " * 10 + "<tr>" + footer + "</tr>"

  def showHTML(self):
    result = ""
    if self.details == True:
      result += "<details open><summary>{summary}</summary>".format(summary = self.summary)
    result += """
      <table class='{tableClass}'>
        <thead>{headers}
        </thead>
        <tbody>{rowContent}
        </tbody>
        <tfoot>{footer}
        </tfoot>
      </table>""".format(tableClass = self.tableClass, headers = self.headers, rowContent = self.rowContent, footer = self.footer)
    if self.details == True:
      result += "\n" + " " * 4 + "</details>"
    return result

""" The Class Form complements the Pi_HTML class to manage forms of different input types"""
class Form:
  def __init__(self, name, action, method, submit):
    self.name = name
    self.action = action
    self.method = method
    self.submit = submit
    self.encType = "application/x-www-form-urlencoded"
    self.button = ""
    self.formContent = ""
    self.extraContent = ""

  def add_extraContent(self, content):
    self.extraContent = "\n" + " " * 8 + content

  def add_item(self, label, name, value, inputType, attributes):
    if inputType == "hidden":
      item = "\n" + " " * 10 + "<input type='{inputType}' name='{name}' value='{value}' />".format(inputType = inputType, value = value, name = name)
    elif inputType == "readonly":
      item = "\n" + " " * 10 + "<tr><th><label for='{name}'>{label}:</label></th>".format(name = name, label = label) + "\n" + " " * 12
      item += "<td class='input_field'><input type='{inputType}' id='{name}' name='{name}' value='{value}' readonly /></td></tr>".format(
        inputType = inputType, value = value, name = name)
    elif inputType == "password":
      item = "\n" + " " * 10 + "<tr><th><label for='{name}'>{label}:</label></th>".format(name = name, label = label) + "\n" + " " * 12
      item += "<td class='input_field'><input type='{inputType}' id='{name}' name='{name}' placeholder='Enter {label}' {attributes} /></td></tr>".format(
        inputType = inputType, name = name, label = label, attributes = attributes)
    elif inputType == "text":
      item = "\n" + " " * 10 + "<tr><th><label for='{name}'>{label}:</label></th>".format(name = name, label = label) + "\n" + " " * 12
      item += """<td class='input_field'>
            <input type='{inputType}' id='{name}' name='{name}' value='{value}' placeholder='Enter {label}' {attributes} />
            </td></tr>""".format(inputType = inputType, name = name, label = label, value = value, attributes = attributes)
    elif inputType == "number":
      item = "\n" + " " * 10 + "<tr><th><label for='{name}'>{label}:</label></th>".format(name = name, label = label) + "\n" + " " * 12
      item += """<td class='input_field'>
            <input type='{inputType}' id='{name}' name='{name}' value='{value}' placeholder='Enter {label}' class='number' {attributes} />
            </td></tr>""".format(inputType = inputType, name = name, label = label, value = value, attributes = attributes)
    elif inputType == "date":
      item = "\n" + " " * 10 + "<tr><th><label for='{name}'>{label}:</label></th>".format(name = name, label = label) + "\n" + " " * 12
      item += """<td class='input_field'>
            <input type='{inputType}' id='{name}' name='{name}' value='{value}' placeholder='Enter {label}' class='date' {attributes} />
            </td></tr>""".format(inputType = inputType, name = name, label = label, value = value, attributes = attributes)
    elif inputType == "file":
      item = "\n" + " " * 10 + "<tr><th><label for='{name}'>{label}:</label></th>".format(name = name, label = label) + "\n" + " " * 12
      item += """<td class='input_field'>
            <input type='{inputType}' id='{name}' name='{name}' placeholder='Choose a file to upload' {attributes} />
            </td></tr>""".format(inputType = inputType, name = name, label = label, value = value, attributes = attributes)
    elif inputType == "picture":
      item = "\n" + " " * 10 + "<tr><th><label for='{name}'>{label}:</label></th>".format(name = name, label = label) + "\n" + " " * 12
      item += """<td class='input_field'>
            <input type='file' id='{name}' name='{name}' placeholder='Choose a picture file to upload' />
            </td></tr>""".format(name = name, label = label, value = value, attributes = attributes)
    elif inputType == "textarea":
      item = "\n" + " " * 10 + "<tr><th><label for='{name}'>{label}:</label></th>".format(name = name, label = label) + "\n" + " " * 12
      item += """<td class='input_field'>
            <textarea id='{name}' name='{name}' placeholder='Enter {label}' rows='2' cols='80' maxlength='250' {attributes} >{value}</textarea>
            </td></tr>""".format(value = value, name = name, label = label, attributes = attributes)
    elif inputType == "select":
      item = "\n" + " " * 10 + "<tr><th><label for='{name}'>{label}:</label></th>".format(name = name, label = label) + "\n" + " " * 12
      item += """<td class='input_field'>
            <select id='{name}' name='{name}' placeholder='Enter {label}' {attributes} >{value}</select></td></tr>""".format(
              value = value, name = name, label = label, attributes = attributes)
    elif inputType == "checkbox":
      item = "\n" + " " * 10 + "<tr><th><label for='{name}'>{label}:</label></th>".format(name = name, label = label) + "\n" + " " * 12
      item += """<td class='input_field'>
            <input type='{inputType}' id='{name}' name='{name}' value='{value}' {attributes} /></td></tr>""".format(
              inputType = inputType, name = name, label = label, value = value, attributes = attributes)
    else:
      item = "\n" + " " * 10 + "<tr><th><label for='{name}'>{label}:</label></th>".format(name = name, label = label) + "\n" + " " * 12
      item += """<td class='input_field'>
            <input type='{inputType}' id='{name}' name='{name}' value='{value}' placeholder='Enter {label}' {attributes} />
            </td></tr>""".format(inputType = inputType, name = name, label = label, value = value, attributes = attributes)
      
    self.formContent += item

  def add_button(self, name):
    self.button += "\n" + " " * 6 + "<button type='submit' name='submit' value='{name}'>{name}</button>".format(name = name)

  def select_options(self, options_array, selected_id, first_empty = True):
    result = ""
    if first_empty == True:
      result += "\n" + "  " * 7 + "<option></option>"
    for each_item in options_array:
      if each_item[0] == selected_id:
        selected = "selected"
      else:
        selected = ""
      result += "\n"+ "  " * 7 + "<option value='{item_id}' {selected}>{item_value}</option>".format(item_id = each_item[0], item_value = each_item[1], selected = selected)
    return result

  def showHTML(self):
    result = "<form name='{name}' id='{name}' action='{action}' method='{method}' onsubmit='return validateForm(this);' enctype='{encType}'>".format(
      name = self.name, action = self.action, method = self.method, encType = self.encType)
    result += """
      <table class='formTable'>
        <tbody>{formContent}
        </tbody>
      </table>""".format(formContent = self.formContent)
    if not self.submit == "":
      result += """
      <button type='submit' name='submit' value='{submit}'>{submit}</button>{button}
      <button type='reset' value='Clear'>Clear</button>""".format(submit = self.submit, button = self.button)
    result += "\n" + " " * 4 + "</form>"
    return result

def fetchPost(wsgi_input):
  bytes2String = ""
  for each_byte in wsgi_input:
    bytes2String = bytes2String + each_byte.decode(encoding='UTF-8')
  rawFields = bytes2String.split("&")
  result = fetchQueryString(rawFields)
  return result

def fetchQueryString(request_data):
  result = {}
  for each_item in request_data:
    (name, value) = each_item.split("=")
    result[name] = urllib.parse.unquote_plus(value)
  return result
