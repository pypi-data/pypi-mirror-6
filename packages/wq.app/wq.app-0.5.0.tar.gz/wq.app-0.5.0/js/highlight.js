define(function() {
var hljs = new function() {

  /* Utility functions */

  function escape(value) {
    return value.replace(/&/gm, '&amp;').replace(/</gm, '&lt;').replace(/>/gm, '&gt;');
  }

  function findCode(pre) {
    for (var node = pre.firstChild; node; node = node.nextSibling) {
      if (node.nodeName.toUpperCase () == 'CODE')
        return node;
      if (!(node.nodeType == 3 && node.nodeValue.match(/\s+/)))
        break;
    }
  }

  function blockText(block, ignoreNewLines) {
    return Array.prototype.map.call(block.childNodes, function(node) {
      if (node.nodeType == 3) {
        return ignoreNewLines ? node.nodeValue.replace(/\n/g, '') : node.nodeValue;
      }
      if (node.nodeName.toUpperCase () == 'BR') {
        return '\n';
      }
      return blockText(node, ignoreNewLines);
    }).join('');
  }

  function blockLanguage(block) {
    var classes = (block.className + ' ' + (block.parentNode ? block.parentNode.className : '')).split(/\s+/);
    classes = classes.map(function(c) {return c.replace(/^language-/, '');});
    for (var i = 0; i < classes.length; i++) {
      if (languages[classes[i]] || classes[i] == 'no-highlight') {
        return classes[i];
      }
    }
  }

  /* Stream merging */

  function nodeStream(node) {
    var result = [];
    (function _nodeStream(node, offset) {
      for (var child = node.firstChild; child; child = child.nextSibling) {
        if (child.nodeType == 3)
          offset += child.nodeValue.length;
        else if (child.nodeName.toUpperCase() == 'BR')
          offset += 1;
        else if (child.nodeType == 1) {
          result.push({
            event: 'start',
            offset: offset,
            node: child
          });
          offset = _nodeStream(child, offset);
          result.push({
            event: 'stop',
            offset: offset,
            node: child
          });
        }
      }
      return offset;
    })(node, 0);
    return result;
  }

  function mergeStreams(original, highlighted, value) {
    var processed = 0;
    var result = '';
    var nodeStack = [];

    function selectStream() {
      if (!original.length || !highlighted.length) {
        return original.length ? original : highlighted;
      }
      if (original[0].offset != highlighted[0].offset) {
        return (original[0].offset < highlighted[0].offset) ? original : highlighted;
      }

      /*
      To avoid starting the stream just before it should stop the order is
      ensured that original always starts first and closes last:

      if (event1 == 'start' && event2 == 'start')
        return original;
      if (event1 == 'start' && event2 == 'stop')
        return highlighted;
      if (event1 == 'stop' && event2 == 'start')
        return original;
      if (event1 == 'stop' && event2 == 'stop')
        return highlighted;

      ... which is collapsed to:
      */
      return highlighted[0].event == 'start' ? original : highlighted;
    }

    function open(node) {
      function attr_str(a) {return ' ' + a.nodeName + '="' + escape(a.value) + '"';}
      result += '<' + node.nodeName.toLowerCase() + Array.prototype.map.call(node.attributes, attr_str).join('') + '>';
    }

    function close(node) {
      result += '</' + node.nodeName.toLowerCase() + '>';
    }

    function render(event) {
      (event.event == 'start' ? open : close)(event.node);
    }

    while (original.length || highlighted.length) {
      var stream = selectStream();
      result += escape(value.substr(processed, stream[0].offset - processed));
      processed = stream[0].offset;
      if (stream == original) {
        /*
        On any opening or closing tag of the original markup we first close
        the entire highlighted node stack, then render the original tag along
        with all the following original tags at the same offset and then
        reopen all the tags on the highlighted stack.
        */
        nodeStack.reverse().forEach(close);
        do {
          render(stream.splice(0, 1)[0]);
          stream = selectStream();
        } while (stream == original && stream.length && stream[0].offset == processed);
        nodeStack.reverse().forEach(open);
      } else {
        if (stream[0].event == 'start') {
          nodeStack.push(stream[0].node);
        } else {
          nodeStack.pop();
        }
        render(stream.splice(0, 1)[0]);
      }
    }
    return result + escape(value.substr(processed));
  }

  /* Initialization */

  function compileLanguage(language) {

    function reStr(re) {
        return (re && re.source) || re;
    }

    function langRe(value, global) {
      return RegExp(
        reStr(value),
        'm' + (language.case_insensitive ? 'i' : '') + (global ? 'g' : '')
      );
    }

    function compileMode(mode, parent) {
      if (mode.compiled)
        return;
      mode.compiled = true;

      var keywords = []; // used later with beginWithKeyword but filled as a side-effect of keywords compilation
      if (mode.keywords) {
        var compiled_keywords = {};

        function flatten(className, str) {
          if (language.case_insensitive) {
            str = str.toLowerCase();
          }
          str.split(' ').forEach(function(kw) {
            var pair = kw.split('|');
            compiled_keywords[pair[0]] = [className, pair[1] ? Number(pair[1]) : 1];
            keywords.push(pair[0]);
          });
        }

        mode.lexemsRe = langRe(mode.lexems || '\\b' + hljs.IDENT_RE + '\\b(?!\\.)', true);
        if (typeof mode.keywords == 'string') { // string
          flatten('keyword', mode.keywords);
        } else {
          for (var className in mode.keywords) {
            if (!mode.keywords.hasOwnProperty(className))
              continue;
            flatten(className, mode.keywords[className]);
          }
        }
        mode.keywords = compiled_keywords;
      }
      if (parent) {
        if (mode.beginWithKeyword) {
          mode.begin = '\\b(' + keywords.join('|') + ')\\b(?!\\.)\\s*';
        }
        mode.beginRe = langRe(mode.begin ? mode.begin : '\\B|\\b');
        if (!mode.end && !mode.endsWithParent)
          mode.end = '\\B|\\b';
        if (mode.end)
          mode.endRe = langRe(mode.end);
        mode.terminator_end = reStr(mode.end) || '';
        if (mode.endsWithParent && parent.terminator_end)
          mode.terminator_end += (mode.end ? '|' : '') + parent.terminator_end;
      }
      if (mode.illegal)
        mode.illegalRe = langRe(mode.illegal);
      if (mode.relevance === undefined)
        mode.relevance = 1;
      if (!mode.contains) {
        mode.contains = [];
      }
      for (var i = 0; i < mode.contains.length; i++) {
        if (mode.contains[i] == 'self') {
          mode.contains[i] = mode;
        }
        compileMode(mode.contains[i], mode);
      }
      if (mode.starts) {
        compileMode(mode.starts, parent);
      }

      var terminators = [];
      for (var i = 0; i < mode.contains.length; i++) {
        terminators.push(reStr(mode.contains[i].begin));
      }
      if (mode.terminator_end) {
        terminators.push(reStr(mode.terminator_end));
      }
      if (mode.illegal) {
        terminators.push(reStr(mode.illegal));
      }
      mode.terminators = terminators.length ? langRe(terminators.join('|'), true) : {exec: function(s) {return null;}};
    }

    compileMode(language);
  }

  /*
  Core highlighting function. Accepts a language name and a string with the
  code to highlight. Returns an object with the following properties:

  - relevance (int)
  - keyword_count (int)
  - value (an HTML string with highlighting markup)

  */
  function highlight(language_name, value, ignore_illegals, continuation) {

    function subMode(lexem, mode) {
      for (var i = 0; i < mode.contains.length; i++) {
        var match = mode.contains[i].beginRe.exec(lexem);
        if (match && match.index == 0) {
          return mode.contains[i];
        }
      }
    }

    function endOfMode(mode, lexem) {
      if (mode.end && mode.endRe.test(lexem)) {
        return mode;
      }
      if (mode.endsWithParent) {
        return endOfMode(mode.parent, lexem);
      }
    }

    function isIllegal(lexem, mode) {
      return !ignore_illegals && mode.illegal && mode.illegalRe.test(lexem);
    }

    function keywordMatch(mode, match) {
      var match_str = language.case_insensitive ? match[0].toLowerCase() : match[0];
      return mode.keywords.hasOwnProperty(match_str) && mode.keywords[match_str];
    }

    function processKeywords() {
      var buffer = escape(mode_buffer);
      if (!top.keywords)
        return buffer;
      var result = '';
      var last_index = 0;
      top.lexemsRe.lastIndex = 0;
      var match = top.lexemsRe.exec(buffer);
      while (match) {
        result += buffer.substr(last_index, match.index - last_index);
        var keyword_match = keywordMatch(top, match);
        if (keyword_match) {
          keyword_count += keyword_match[1];
          result += '<span class="'+ keyword_match[0] +'">' + match[0] + '</span>';
        } else {
          result += match[0];
        }
        last_index = top.lexemsRe.lastIndex;
        match = top.lexemsRe.exec(buffer);
      }
      return result + buffer.substr(last_index);
    }

    function processSubLanguage() {
      if (top.subLanguage && !languages[top.subLanguage]) {
        return escape(mode_buffer);
      }
      var continuation = top.subLanguageMode == 'continuous' ? top.top : undefined;
      var result = top.subLanguage ? highlight(top.subLanguage, mode_buffer, true, continuation) : highlightAuto(mode_buffer);
      // Counting embedded language score towards the host language may be disabled
      // with zeroing the containing mode relevance. Usecase in point is Markdown that
      // allows XML everywhere and makes every XML snippet to have a much larger Markdown
      // score.
      if (top.relevance > 0) {
        keyword_count += result.keyword_count;
        relevance += result.relevance;
      }
      top.top = result.top;
      return '<span class="' + result.language  + '">' + result.value + '</span>';
    }

    function processBuffer() {
      return top.subLanguage !== undefined ? processSubLanguage() : processKeywords();
    }

    function startNewMode(mode, lexem) {
      var markup = mode.className? '<span class="' + mode.className + '">': '';
      if (mode.returnBegin) {
        result += markup;
        mode_buffer = '';
      } else if (mode.excludeBegin) {
        result += escape(lexem) + markup;
        mode_buffer = '';
      } else {
        result += markup;
        mode_buffer = lexem;
      }
      top = Object.create(mode, {parent: {value: top}});
    }

    function processLexem(buffer, lexem) {
      mode_buffer += buffer;
      if (lexem === undefined) {
        result += processBuffer();
        return 0;
      }

      var new_mode = subMode(lexem, top);
      if (new_mode) {
        result += processBuffer();
        startNewMode(new_mode, lexem);
        return new_mode.returnBegin ? 0 : lexem.length;
      }

      var end_mode = endOfMode(top, lexem);
      if (end_mode) {
        var origin = top;
        if (!(origin.returnEnd || origin.excludeEnd)) {
          mode_buffer += lexem;
        }
        result += processBuffer();
        do {
          if (top.className) {
            result += '</span>';
          }
          relevance += top.relevance;
          top = top.parent;
        } while (top != end_mode.parent);
        if (origin.excludeEnd) {
          result += escape(lexem);
        }
        mode_buffer = '';
        if (end_mode.starts) {
          startNewMode(end_mode.starts, '');
        }
        return origin.returnEnd ? 0 : lexem.length;
      }

      if (isIllegal(lexem, top))
        throw new Error('Illegal lexem "' + lexem + '" for mode "' + (top.className || '<unnamed>') + '"');

      /*
      Parser should not reach this point as all types of lexems should be caught
      earlier, but if it does due to some bug make sure it advances at least one
      character forward to prevent infinite looping.
      */
      mode_buffer += lexem;
      return lexem.length || 1;
    }

    var language = languages[language_name];
    if (!language) {
      throw new Error('Unknown language: "' + language_name + '"');
    }

    compileLanguage(language);
    var top = continuation || language;
    var result = '';
    for(var current = top; current != language; current = current.parent) {
      if (current.className) {
        result = '<span class="' + current.className +'">' + result;
      }
    }
    var mode_buffer = '';
    var relevance = 0;
    var keyword_count = 0;
    try {
      var match, count, index = 0;
      while (true) {
        top.terminators.lastIndex = index;
        match = top.terminators.exec(value);
        if (!match)
          break;
        count = processLexem(value.substr(index, match.index - index), match[0]);
        index = match.index + count;
      }
      processLexem(value.substr(index));
      for(var current = top; current.parent; current = current.parent) { // close dangling modes
        if (current.className) {
          result += '</span>';
        }
      };
      return {
        relevance: relevance,
        keyword_count: keyword_count,
        value: result,
        language: language_name,
        top: top
      };
    } catch (e) {
      if (e.message.indexOf('Illegal') != -1) {
        return {
          relevance: 0,
          keyword_count: 0,
          value: escape(value)
        };
      } else {
        throw e;
      }
    }
  }

  /*
  Highlighting with language detection. Accepts a string with the code to
  highlight. Returns an object with the following properties:

  - language (detected language)
  - relevance (int)
  - keyword_count (int)
  - value (an HTML string with highlighting markup)
  - second_best (object with the same structure for second-best heuristically
    detected language, may be absent)

  */
  function highlightAuto(text) {
    var result = {
      keyword_count: 0,
      relevance: 0,
      value: escape(text)
    };
    var second_best = result;
    for (var key in languages) {
      if (!languages.hasOwnProperty(key))
        continue;
      var current = highlight(key, text, false);
      current.language = key;
      if (current.keyword_count + current.relevance > second_best.keyword_count + second_best.relevance) {
        second_best = current;
      }
      if (current.keyword_count + current.relevance > result.keyword_count + result.relevance) {
        second_best = result;
        result = current;
      }
    }
    if (second_best.language) {
      result.second_best = second_best;
    }
    return result;
  }

  /*
  Post-processing of the highlighted markup:

  - replace TABs with something more useful
  - replace real line-breaks with '<br>' for non-pre containers

  */
  function fixMarkup(value, tabReplace, useBR) {
    if (tabReplace) {
      value = value.replace(/^((<[^>]+>|\t)+)/gm, function(match, p1, offset, s) {
        return p1.replace(/\t/g, tabReplace);
      });
    }
    if (useBR) {
      value = value.replace(/\n/g, '<br>');
    }
    return value;
  }

  /*
  Applies highlighting to a DOM node containing code. Accepts a DOM node and
  two optional parameters for fixMarkup.
  */
  function highlightBlock(block, tabReplace, useBR) {
    var text = blockText(block, useBR);
    var language = blockLanguage(block);
    if (language == 'no-highlight')
        return;
    var result = language ? highlight(language, text, true) : highlightAuto(text);
    language = result.language;
    var original = nodeStream(block);
    if (original.length) {
      var pre = document.createElementNS('http://www.w3.org/1999/xhtml', 'pre');
      pre.innerHTML = result.value;
      result.value = mergeStreams(original, nodeStream(pre), text);
    }
    result.value = fixMarkup(result.value, tabReplace, useBR);

    var class_name = block.className;
    if (!class_name.match('(\\s|^)(language-)?' + language + '(\\s|$)')) {
      class_name = class_name ? (class_name + ' ' + language) : language;
    }
    block.innerHTML = result.value;
    block.className = class_name;
    block.result = {
      language: language,
      kw: result.keyword_count,
      re: result.relevance
    };
    if (result.second_best) {
      block.second_best = {
        language: result.second_best.language,
        kw: result.second_best.keyword_count,
        re: result.second_best.relevance
      };
    }
  }

  /*
  Applies highlighting to all <pre><code>..</code></pre> blocks on a page.
  */
  function initHighlighting() {
    if (initHighlighting.called)
      return;
    initHighlighting.called = true;
    Array.prototype.map.call(document.getElementsByTagNameNS('http://www.w3.org/1999/xhtml', 'pre'), findCode).
      filter(Boolean).
      forEach(function(code){highlightBlock(code, hljs.tabReplace);});
  }

  /*
  Attaches highlighting to the page load event.
  */
  function initHighlightingOnLoad() {
    window.addEventListener('DOMContentLoaded', initHighlighting, false);
    window.addEventListener('load', initHighlighting, false);
  }

  var languages = {}; // a shortcut to avoid writing "this." everywhere

  /* Interface definition */

  this.LANGUAGES = languages;
  this.highlight = highlight;
  this.highlightAuto = highlightAuto;
  this.fixMarkup = fixMarkup;
  this.highlightBlock = highlightBlock;
  this.initHighlighting = initHighlighting;
  this.initHighlightingOnLoad = initHighlightingOnLoad;

  // Common regexps
  this.IDENT_RE = '[a-zA-Z][a-zA-Z0-9_]*';
  this.UNDERSCORE_IDENT_RE = '[a-zA-Z_][a-zA-Z0-9_]*';
  this.NUMBER_RE = '\\b\\d+(\\.\\d+)?';
  this.C_NUMBER_RE = '(\\b0[xX][a-fA-F0-9]+|(\\b\\d+(\\.\\d*)?|\\.\\d+)([eE][-+]?\\d+)?)'; // 0x..., 0..., decimal, float
  this.BINARY_NUMBER_RE = '\\b(0b[01]+)'; // 0b...
  this.RE_STARTERS_RE = '!|!=|!==|%|%=|&|&&|&=|\\*|\\*=|\\+|\\+=|,|\\.|-|-=|/|/=|:|;|<<|<<=|<=|<|===|==|=|>>>=|>>=|>=|>>>|>>|>|\\?|\\[|\\{|\\(|\\^|\\^=|\\||\\|=|\\|\\||~';

  // Common modes
  this.BACKSLASH_ESCAPE = {
    begin: '\\\\[\\s\\S]', relevance: 0
  };
  this.APOS_STRING_MODE = {
    className: 'string',
    begin: '\'', end: '\'',
    illegal: '\\n',
    contains: [this.BACKSLASH_ESCAPE],
    relevance: 0
  };
  this.QUOTE_STRING_MODE = {
    className: 'string',
    begin: '"', end: '"',
    illegal: '\\n',
    contains: [this.BACKSLASH_ESCAPE],
    relevance: 0
  };
  this.C_LINE_COMMENT_MODE = {
    className: 'comment',
    begin: '//', end: '$'
  };
  this.C_BLOCK_COMMENT_MODE = {
    className: 'comment',
    begin: '/\\*', end: '\\*/'
  };
  this.HASH_COMMENT_MODE = {
    className: 'comment',
    begin: '#', end: '$'
  };
  this.NUMBER_MODE = {
    className: 'number',
    begin: this.NUMBER_RE,
    relevance: 0
  };
  this.C_NUMBER_MODE = {
    className: 'number',
    begin: this.C_NUMBER_RE,
    relevance: 0
  };
  this.BINARY_NUMBER_MODE = {
    className: 'number',
    begin: this.BINARY_NUMBER_RE,
    relevance: 0
  };
  this.REGEXP_MODE = {
    className: 'regexp',
    begin: /\//, end: /\/[gim]*/,
    illegal: /\n/,
    contains: [
      this.BACKSLASH_ESCAPE,
      {
        begin: /\[/, end: /\]/,
        relevance: 0,
        contains: [this.BACKSLASH_ESCAPE]
      }
    ]
  };

  // Utility functions
  this.inherit = function(parent, obj) {
    var result = {};
    for (var key in parent)
      result[key] = parent[key];
    if (obj)
      for (var key in obj)
        result[key] = obj[key];
    return result;
  };
}();
hljs.LANGUAGES['xml'] = function(hljs) {
  var XML_IDENT_RE = '[A-Za-z0-9\\._:-]+';
  var TAG_INTERNALS = {
    endsWithParent: true,
    relevance: 0,
    contains: [
      {
        className: 'attribute',
        begin: XML_IDENT_RE,
        relevance: 0
      },
      {
        begin: '="', returnBegin: true, end: '"',
        contains: [{
            className: 'value',
            begin: '"', endsWithParent: true
        }]
      },
      {
        begin: '=\'', returnBegin: true, end: '\'',
        contains: [{
          className: 'value',
          begin: '\'', endsWithParent: true
        }]
      },
      {
        begin: '=',
        contains: [{
          className: 'value',
          begin: '[^\\s/>]+'
        }]
      }
    ]
  };
  return {
    case_insensitive: true,
    contains: [
      {
        className: 'pi',
        begin: '<\\?', end: '\\?>',
        relevance: 10
      },
      {
        className: 'doctype',
        begin: '<!DOCTYPE', end: '>',
        relevance: 10,
        contains: [{begin: '\\[', end: '\\]'}]
      },
      {
        className: 'comment',
        begin: '<!--', end: '-->',
        relevance: 10
      },
      {
        className: 'cdata',
        begin: '<\\!\\[CDATA\\[', end: '\\]\\]>',
        relevance: 10
      },
      {
        className: 'tag',
        /*
        The lookahead pattern (?=...) ensures that 'begin' only matches
        '<style' as a single word, followed by a whitespace or an
        ending braket. The '$' is needed for the lexem to be recognized
        by hljs.subMode() that tests lexems outside the stream.
        */
        begin: '<style(?=\\s|>|$)', end: '>',
        keywords: {title: 'style'},
        contains: [TAG_INTERNALS],
        starts: {
          end: '</style>', returnEnd: true,
          subLanguage: 'css'
        }
      },
      {
        className: 'tag',
        // See the comment in the <style tag about the lookahead pattern
        begin: '<script(?=\\s|>|$)', end: '>',
        keywords: {title: 'script'},
        contains: [TAG_INTERNALS],
        starts: {
          end: '</script>', returnEnd: true,
          subLanguage: 'javascript'
        }
      },
      {
        begin: '<%', end: '%>',
        subLanguage: 'vbscript'
      },
      {
        className: 'tag',
        begin: '</?', end: '/?>',
        relevance: 0,
        contains: [
          {
            className: 'title', begin: '[^ /><]+'
          },
          TAG_INTERNALS
        ]
      }
    ]
  };
}(hljs);
hljs.LANGUAGES['markdown'] = function(hljs) {
  return {
    contains: [
      // highlight headers
      {
        className: 'header',
        begin: '^#{1,3}', end: '$'
      },
      {
        className: 'header',
        begin: '^.+?\\n[=-]{2,}$'
      },
      // inline html
      {
        begin: '<', end: '>',
        subLanguage: 'xml',
        relevance: 0
      },
      // lists (indicators only)
      {
        className: 'bullet',
        begin: '^([*+-]|(\\d+\\.))\\s+'
      },
      // strong segments
      {
        className: 'strong',
        begin: '[*_]{2}.+?[*_]{2}'
      },
      // emphasis segments
      {
        className: 'emphasis',
        begin: '\\*.+?\\*'
      },
      {
        className: 'emphasis',
        begin: '_.+?_',
        relevance: 0
      },
      // blockquotes
      {
        className: 'blockquote',
        begin: '^>\\s+', end: '$'
      },
      // code snippets
      {
        className: 'code',
        begin: '`.+?`'
      },
      {
        className: 'code',
        begin: '^    ', end: '$',
        relevance: 0
      },
      // horizontal rules
      {
        className: 'horizontal_rule',
        begin: '^-{3,}', end: '$'
      },
      // using links - title and link
      {
        begin: '\\[.+?\\]\\(.+?\\)',
        returnBegin: true,
        contains: [
          {
            className: 'link_label',
            begin: '\\[.+\\]'
          },
          {
            className: 'link_url',
            begin: '\\(', end: '\\)',
            excludeBegin: true, excludeEnd: true
          }
        ]
      }
    ]
  };
}(hljs);
hljs.LANGUAGES['python'] = function(hljs) {
  var PROMPT = {
    className: 'prompt',  begin: /^(>>>|\.\.\.) /
  }
  var STRINGS = [
    {
      className: 'string',
      begin: /(u|b)?r?'''/, end: /'''/,
      contains: [PROMPT],
      relevance: 10
    },
    {
      className: 'string',
      begin: /(u|b)?r?"""/, end: /"""/,
      contains: [PROMPT],
      relevance: 10
    },
    {
      className: 'string',
      begin: /(u|r|ur)'/, end: /'/,
      contains: [hljs.BACKSLASH_ESCAPE],
      relevance: 10
    },
    {
      className: 'string',
      begin: /(u|r|ur)"/, end: /"/,
      contains: [hljs.BACKSLASH_ESCAPE],
      relevance: 10
    },
    {
      className: 'string',
      begin: /(b|br)'/, end: /'/,
      contains: [hljs.BACKSLASH_ESCAPE]
    },
    {
      className: 'string',
      begin: /(b|br)"/, end: /"/,
      contains: [hljs.BACKSLASH_ESCAPE]
    }
  ].concat([
    hljs.APOS_STRING_MODE,
    hljs.QUOTE_STRING_MODE
  ]);
  var TITLE = {
    className: 'title', begin: hljs.UNDERSCORE_IDENT_RE
  };
  var PARAMS = {
    className: 'params',
    begin: /\(/, end: /\)/,
    contains: ['self', hljs.C_NUMBER_MODE, PROMPT].concat(STRINGS)
  };
  var FUNC_CLASS_PROTO = {
    beginWithKeyword: true, end: /:/,
    illegal: /[${=;\n]/,
    contains: [TITLE, PARAMS],
    relevance: 10
  };

  return {
    keywords: {
      keyword:
        'and elif is global as in if from raise for except finally print import pass return ' +
        'exec else break not with class assert yield try while continue del or def lambda ' +
        'nonlocal|10 None True False',
      built_in:
        'Ellipsis NotImplemented'
    },
    illegal: /(<\/|->|\?)/,
    contains: STRINGS.concat([
      PROMPT,
      hljs.HASH_COMMENT_MODE,
      hljs.inherit(FUNC_CLASS_PROTO, {className: 'function', keywords: 'def'}),
      hljs.inherit(FUNC_CLASS_PROTO, {className: 'class', keywords: 'class'}),
      hljs.C_NUMBER_MODE,
      {
        className: 'decorator',
        begin: /@/, end: /$/
      },
      {
        begin: /\b(print|exec)\(/ // don’t highlight keywords-turned-functions in Python 3
      }
    ])
  };
}(hljs);
hljs.LANGUAGES['css'] = function(hljs) {
  var IDENT_RE = '[a-zA-Z-][a-zA-Z0-9_-]*';
  var FUNCTION = {
    className: 'function',
    begin: IDENT_RE + '\\(', end: '\\)',
    contains: ['self', hljs.NUMBER_MODE, hljs.APOS_STRING_MODE, hljs.QUOTE_STRING_MODE]
  };
  return {
    case_insensitive: true,
    illegal: '[=/|\']',
    contains: [
      hljs.C_BLOCK_COMMENT_MODE,
      {
        className: 'id', begin: '\\#[A-Za-z0-9_-]+'
      },
      {
        className: 'class', begin: '\\.[A-Za-z0-9_-]+',
        relevance: 0
      },
      {
        className: 'attr_selector',
        begin: '\\[', end: '\\]',
        illegal: '$'
      },
      {
        className: 'pseudo',
        begin: ':(:)?[a-zA-Z0-9\\_\\-\\+\\(\\)\\"\\\']+'
      },
      {
        className: 'at_rule',
        begin: '@(font-face|page)',
        lexems: '[a-z-]+',
        keywords: 'font-face page'
      },
      {
        className: 'at_rule',
        begin: '@', end: '[{;]', // at_rule eating first "{" is a good thing
                                 // because it doesn’t let it to be parsed as
                                 // a rule set but instead drops parser into
                                 // the default mode which is how it should be.
        contains: [
          {
            className: 'keyword',
            begin: /\S+/
          },
          {
            begin: /\s/, endsWithParent: true, excludeEnd: true,
            relevance: 0,
            contains: [
              FUNCTION,
              hljs.APOS_STRING_MODE, hljs.QUOTE_STRING_MODE,
              hljs.NUMBER_MODE
            ]
          }
        ]
      },
      {
        className: 'tag', begin: IDENT_RE,
        relevance: 0
      },
      {
        className: 'rules',
        begin: '{', end: '}',
        illegal: '[^\\s]',
        relevance: 0,
        contains: [
          hljs.C_BLOCK_COMMENT_MODE,
          {
            className: 'rule',
            begin: '[^\\s]', returnBegin: true, end: ';', endsWithParent: true,
            contains: [
              {
                className: 'attribute',
                begin: '[A-Z\\_\\.\\-]+', end: ':',
                excludeEnd: true,
                illegal: '[^\\s]',
                starts: {
                  className: 'value',
                  endsWithParent: true, excludeEnd: true,
                  contains: [
                    FUNCTION,
                    hljs.NUMBER_MODE,
                    hljs.QUOTE_STRING_MODE,
                    hljs.APOS_STRING_MODE,
                    hljs.C_BLOCK_COMMENT_MODE,
                    {
                      className: 'hexcolor', begin: '#[0-9A-Fa-f]+'
                    },
                    {
                      className: 'important', begin: '!important'
                    }
                  ]
                }
              }
            ]
          }
        ]
      }
    ]
  };
}(hljs);
hljs.LANGUAGES['bash'] = function(hljs) {
  var VAR1 = {
    className: 'variable', begin: /\$[\w\d#@][\w\d_]*/
  };
  var VAR2 = {
    className: 'variable', begin: /\$\{(.*?)\}/
  };
  var QUOTE_STRING = {
    className: 'string',
    begin: /"/, end: /"/,
    contains: [
      hljs.BACKSLASH_ESCAPE,
      VAR1,
      VAR2,
      {
        className: 'variable',
        begin: /\$\(/, end: /\)/,
        contains: hljs.BACKSLASH_ESCAPE
      }
    ],
    relevance: 0
  };
  var APOS_STRING = {
    className: 'string',
    begin: /'/, end: /'/,
    relevance: 0
  };

  return {
    lexems: /-?[a-z]+/,
    keywords: {
      keyword:
        'if then else elif fi for break continue while in do done exit return set '+
        'declare case esac export exec',
      literal:
        'true false',
      built_in:
        'printf echo read cd pwd pushd popd dirs let eval unset typeset readonly '+
        'getopts source shopt caller type hash bind help sudo',
      operator:
        '-ne -eq -lt -gt -f -d -e -s -l -a' // relevance booster
    },
    contains: [
      {
        className: 'shebang',
        begin: /^#![^\n]+sh\s*$/,
        relevance: 10
      },
      {
        className: 'function',
        begin: /\w[\w\d_]*\s*\(\s*\)\s*\{/,
        returnBegin: true,
        contains: [{className: 'title', begin: /\w[\w\d_]*/}],
        relevance: 0
      },
      hljs.HASH_COMMENT_MODE,
      hljs.NUMBER_MODE,
      QUOTE_STRING,
      APOS_STRING,
      VAR1,
      VAR2
    ]
  };
}(hljs);
hljs.LANGUAGES['scss'] = function(hljs) {
  var IDENT_RE = '[a-zA-Z-][a-zA-Z0-9_-]*';
  var FUNCTION = {
    className: 'function',
    begin: IDENT_RE + '\\(', end: '\\)',
    contains: ['self', hljs.NUMBER_MODE, hljs.APOS_STRING_MODE, hljs.QUOTE_STRING_MODE]
  };
  var HEXCOLOR = {
    className: 'hexcolor', begin: '#[0-9A-Fa-f]+'
  };
  var DEF_INTERNALS = {
    className: 'attribute',
    begin: '[A-Z\\_\\.\\-]+', end: ':',
    excludeEnd: true,
    illegal: '[^\\s]',
    starts: {
      className: 'value',
      endsWithParent: true, excludeEnd: true,
      contains: [
        FUNCTION,
        HEXCOLOR,
        hljs.NUMBER_MODE,
        hljs.QUOTE_STRING_MODE,
        hljs.APOS_STRING_MODE,
        hljs.C_BLOCK_COMMENT_MODE,
        {
          className: 'important', begin: '!important'
        }
      ]
    }
  };
  return {
    case_insensitive: true,
    illegal: '[=/|\']',
    contains: [
      hljs.C_LINE_COMMENT_MODE,
      hljs.C_BLOCK_COMMENT_MODE,
      {
        className: 'function',
        begin: IDENT_RE + '\\(', end: '\\)',
        contains: ['self', hljs.NUMBER_MODE, hljs.APOS_STRING_MODE, hljs.QUOTE_STRING_MODE]
      },
      {
        className: 'id', begin: '\\#[A-Za-z0-9_-]+',
        relevance: 0
      },
      {
        className: 'class', begin: '\\.[A-Za-z0-9_-]+',
        relevance: 0
      },
      {
        className: 'attr_selector',
        begin: '\\[', end: '\\]',
        illegal: '$'
      },
      {
        className: 'tag', // begin: IDENT_RE, end: '[,|\\s]'
        begin: '\\b(a|abbr|acronym|address|area|article|aside|audio|b|base|big|blockquote|body|br|button|canvas|caption|cite|code|col|colgroup|command|datalist|dd|del|details|dfn|div|dl|dt|em|embed|fieldset|figcaption|figure|footer|form|frame|frameset|(h[1-6])|head|header|hgroup|hr|html|i|iframe|img|input|ins|kbd|keygen|label|legend|li|link|map|mark|meta|meter|nav|noframes|noscript|object|ol|optgroup|option|output|p|param|pre|progress|q|rp|rt|ruby|samp|script|section|select|small|span|strike|strong|style|sub|sup|table|tbody|td|textarea|tfoot|th|thead|time|title|tr|tt|ul|var|video)\\b',
        relevance: 0
      },
      {
        className: 'pseudo',
        begin: ':(visited|valid|root|right|required|read-write|read-only|out-range|optional|only-of-type|only-child|nth-of-type|nth-last-of-type|nth-last-child|nth-child|not|link|left|last-of-type|last-child|lang|invalid|indeterminate|in-range|hover|focus|first-of-type|first-line|first-letter|first-child|first|enabled|empty|disabled|default|checked|before|after|active)'
      },
      {
        className: 'pseudo',
        begin: '::(after|before|choices|first-letter|first-line|repeat-index|repeat-item|selection|value)'
      },
      {
        className: 'attribute',
        begin: '\\b(z-index|word-wrap|word-spacing|word-break|width|widows|white-space|visibility|vertical-align|unicode-bidi|transition-timing-function|transition-property|transition-duration|transition-delay|transition|transform-style|transform-origin|transform|top|text-underline-position|text-transform|text-shadow|text-rendering|text-overflow|text-indent|text-decoration-style|text-decoration-line|text-decoration-color|text-decoration|text-align-last|text-align|tab-size|table-layout|right|resize|quotes|position|pointer-events|perspective-origin|perspective|page-break-inside|page-break-before|page-break-after|padding-top|padding-right|padding-left|padding-bottom|padding|overflow-y|overflow-x|overflow-wrap|overflow|outline-width|outline-style|outline-offset|outline-color|outline|orphans|order|opacity|object-position|object-fit|normal|none|nav-up|nav-right|nav-left|nav-index|nav-down|min-width|min-height|max-width|max-height|mask|marks|margin-top|margin-right|margin-left|margin-bottom|margin|list-style-type|list-style-position|list-style-image|list-style|line-height|letter-spacing|left|justify-content|initial|inherit|ime-mode|image-orientation|image-resolution|image-rendering|icon|hyphens|height|font-weight|font-variant-ligatures|font-variant|font-style|font-stretch|font-size-adjust|font-size|font-language-override|font-kerning|font-feature-settings|font-family|font|float|flex-wrap|flex-shrink|flex-grow|flex-flow|flex-direction|flex-basis|flex|filter|empty-cells|display|direction|cursor|counter-reset|counter-increment|content|column-width|column-span|column-rule-width|column-rule-style|column-rule-color|column-rule|column-gap|column-fill|column-count|columns|color|clip-path|clip|clear|caption-side|break-inside|break-before|break-after|box-sizing|box-shadow|box-decoration-break|bottom|border-width|border-top-width|border-top-style|border-top-right-radius|border-top-left-radius|border-top-color|border-top|border-style|border-spacing|border-right-width|border-right-style|border-right-color|border-right|border-radius|border-left-width|border-left-style|border-left-color|border-left|border-image-width|border-image-source|border-image-slice|border-image-repeat|border-image-outset|border-image|border-color|border-collapse|border-bottom-width|border-bottom-style|border-bottom-right-radius|border-bottom-left-radius|border-bottom-color|border-bottom|border|background-size|background-repeat|background-position|background-origin|background-image|background-color|background-clip|background-attachment|background|backface-visibility|auto|animation-timing-function|animation-play-state|animation-name|animation-iteration-count|animation-fill-mode|animation-duration|animation-direction|animation-delay|animation|align-self|align-items|align-content)\\b',
        illegal: '[^\\s]'
      },
      {
        className: 'value',
        begin: '\\b(whitespace|wait|w-resize|visible|vertical-text|vertical-ideographic|uppercase|upper-roman|upper-alpha|underline|transparent|top|thin|thick|text|text-top|text-bottom|tb-rl|table-header-group|table-footer-group|sw-resize|super|strict|static|square|solid|small-caps|separate|se-resize|scroll|s-resize|rtl|row-resize|ridge|right|repeat|repeat-y|repeat-x|relative|progress|pointer|overline|outside|outset|oblique|nowrap|not-allowed|normal|none|nw-resize|no-repeat|no-drop|newspaper|ne-resize|n-resize|move|middle|medium|ltr|lr-tb|lowercase|lower-roman|lower-alpha|loose|list-item|line|line-through|line-edge|lighter|left|keep-all|justify|italic|inter-word|inter-ideograph|inside|inset|inline|inline-block|inherit|inactive|ideograph-space|ideograph-parenthesis|ideograph-numeric|ideograph-alpha|horizontal|hidden|help|hand|groove|fixed|ellipsis|e-resize|double|dotted|distribute|distribute-space|distribute-letter|distribute-all-lines|disc|disabled|default|decimal|dashed|crosshair|collapse|col-resize|circle|char|center|capitalize|break-word|break-all|bottom|both|bolder|bold|block|bidi-override|below|baseline|auto|always|all-scroll|absolute|table|table-cell)\\b'
      },
      {
        className: 'value',
        begin: ':', end: ';',
        contains: [
          HEXCOLOR,
          hljs.NUMBER_MODE,
          hljs.QUOTE_STRING_MODE,
          hljs.APOS_STRING_MODE,
          {
            className: 'important', begin: '!important'
          }
        ]
      },
      {
        className: 'at_rule',
        begin: '@', end: '[{;]',
        keywords: 'mixin include extend for if else each while charset import debug media page content font-face namespace warn',
        contains: [
          FUNCTION,
          hljs.QUOTE_STRING_MODE,
          hljs.APOS_STRING_MODE,
          HEXCOLOR,
          hljs.NUMBER_MODE,
          {
            className: 'preprocessor',
            begin: '\\s[A-Za-z0-9_.-]+',
            relevance: 0
          }
        ]
      }
    ]
  };
}(hljs);
hljs.LANGUAGES['javascript'] = function(hljs) {
  return {
    keywords: {
      keyword:
        'in if for while finally var new function do return void else break catch ' +
        'instanceof with throw case default try this switch continue typeof delete ' +
        'let yield const',
      literal:
        'true false null undefined NaN Infinity'
    },
    contains: [
      hljs.APOS_STRING_MODE,
      hljs.QUOTE_STRING_MODE,
      hljs.C_LINE_COMMENT_MODE,
      hljs.C_BLOCK_COMMENT_MODE,
      hljs.C_NUMBER_MODE,
      { // "value" container
        begin: '(' + hljs.RE_STARTERS_RE + '|\\b(case|return|throw)\\b)\\s*',
        keywords: 'return throw case',
        contains: [
          hljs.C_LINE_COMMENT_MODE,
          hljs.C_BLOCK_COMMENT_MODE,
          hljs.REGEXP_MODE,
          { // E4X
            begin: /</, end: />;/,
            subLanguage: 'xml'
          }
        ],
        relevance: 0
      },
      {
        className: 'function',
        beginWithKeyword: true, end: /{/,
        keywords: 'function',
        contains: [
          {
            className: 'title', begin: /[A-Za-z$_][0-9A-Za-z$_]*/
          },
          {
            className: 'params',
            begin: /\(/, end: /\)/,
            contains: [
              hljs.C_LINE_COMMENT_MODE,
              hljs.C_BLOCK_COMMENT_MODE
            ],
            illegal: /["'\(]/
          }
        ],
        illegal: /\[|%/
      }
    ]
  };
}(hljs);

return hljs;
});