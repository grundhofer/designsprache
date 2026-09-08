"""Generated-document contracts for the new editorial levels."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import unittest
import re
from urllib.parse import urlsplit

from explorer.catalog import CONTEXTS, PRINCIPLES
import build


class Page(HTMLParser):
    VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
    def __init__(self):
        super().__init__()
        self.stack=[]; self.errors=[]; self.ids=[]; self.links=[]; self.main=0; self.h1=0; self.levels=[]; self.visible=[]
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if 'id' in attrs: self.ids.append(attrs['id'])
        if tag=='a': self.links.append(attrs.get('href',''))
        if tag=='main': self.main+=1
        if tag=='h1': self.h1+=1
        if 'data-level' in attrs: self.levels.append(attrs['data-level'])
        if tag not in self.VOID: self.stack.append(tag)
    def handle_data(self, text):
        if not {"script","style"}.intersection(self.stack): self.visible.append(text)
    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1]!=tag: self.errors.append((tag,self.stack[-3:]))
        else: self.stack.pop()


class ExplorerChecks(unittest.TestCase):
    def test_generated_pages_have_balanced_landmarks_and_no_duplicate_ids(self):
        for lang in ('de','en'):
            page=Page(); page.feed((build.DOCS/lang/'index.html').read_text())
            self.assertEqual(page.errors, [], lang)
            self.assertEqual(page.stack, [], lang)
            self.assertEqual((page.main,page.h1),(1,1),lang)
            self.assertEqual(page.levels,['styles','principles','contexts'],lang)
            self.assertEqual([k for k,v in Counter(page.ids).items() if v>1],[],lang)
            for link in page.links:
                if link.startswith('?level=') and '#' in link:
                    self.assertIn(urlsplit(link).fragment,page.ids,link)

    def test_english_visible_copy_has_no_german_chrome(self):
        page=Page(); page.feed((build.DOCS/"en"/"index.html").read_text())
        self.assertIsNone(re.search(r"\b(und|nicht|Oberfläche|Einträge|Haltbarkeit)\b", " ".join(page.visible)))

    def test_context_references_and_bilingual_content_are_complete(self):
        slugs={s for _,_,group in build.ORDER_DE for s in group}
        principles={p[0] for p in PRINCIPLES}
        self.assertEqual(len(principles),6)
        self.assertEqual(len({c['id'] for c in CONTEXTS}),8)
        for c in CONTEXTS:
            self.assertIn(c['principle'],principles)
            self.assertTrue(set(c['styles']) <= slugs,c['id'])
            for key in ['name','tagline','task','limit']:
                self.assertEqual(len(c[key]),2)
                self.assertTrue(all(c[key]))
            self.assertTrue(c['source'][1].startswith('https://'))
            self.assertTrue(all(len(rule)==2 and all(rule) for rule in c['rules']))

    def test_readable_contexts_do_not_require_javascript(self):
        for lang in ('de','en'):
            page=(build.DOCS/lang/'index.html').read_text()
            for c in CONTEXTS:
                self.assertIn(c['task'][lang=='en'],page)
                self.assertIn(c['source'][1],page)
            for key in ['styles','principles','contexts']:
                self.assertNotIn(f'id="{key}" data-level="{key}" hidden',page)
            self.assertIn('<noscript>',page)

if __name__=='__main__': unittest.main()
