// Used to build CodeMirror

import {EditorView, basicSetup} from "codemirror"
import {keymap} from '@codemirror/view'
import {indentWithTab} from "@codemirror/commands"
import {EditorState, Compartment} from "@codemirror/state"
import {javascript} from "@codemirror/lang-javascript"
import {python} from "@codemirror/lang-python"
import {css} from "@codemirror/lang-css"
import {cpp} from "@codemirror/lang-cpp"
import {html} from "@codemirror/lang-html"
import {java} from "@codemirror/lang-java"
import {json} from "@codemirror/lang-json"
import {markdown} from "@codemirror/lang-markdown"
import {php} from "@codemirror/lang-php"
import {rust} from "@codemirror/lang-rust"
import {xml} from "@codemirror/lang-xml"

const submitButton = document.querySelector("#submit-paste");
const editorSource = document.querySelector("#id_content");
editorSource.setAttribute("hidden", "true");

const editorTarget = document.querySelector("#editorTarget");

const syntax = document.querySelector("#id_syntax");

let language = new Compartment;

let languages_mapping = {
  css: css(),
  cpp: cpp(),
  c: cpp(),
  html: html(),
  java: java(),
  javascript: javascript(),
  json: json(),
  markdown: markdown(),
  php: php(),
  python: python(),
  rust: rust(),
  xml: xml(),
}

let config = [];
if (syntax.value in languages_mapping) {
  config = languages_mapping[syntax.value];
}

let state = EditorState.create({
  doc: editorSource.value,
  extensions: [basicSetup, keymap.of([indentWithTab]), language.of(config)],
})

let view = new EditorView({
  state,
  parent: editorTarget
})

const syncEditor = (event) => {
  event.preventDefault();
  editorSource.value = view.state.doc.toString();
  event.originalTarget.form.submit();
};

submitButton.addEventListener("click", syncEditor);

$('#id_syntax').on('select2:select', function (e) {
  config = null;
  if (syntax.value in languages_mapping) {
    config = languages_mapping[syntax.value];
  }
  view.dispatch({
    effects: language.reconfigure(config)
  })
});