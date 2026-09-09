"""Contrast checks for shared viewer text roles, independent of reference styles."""
import unittest
from viewer.theme import PALETTES


def luminance(color):
    values=[int(color[i:i+2],16)/255 for i in (1,3,5)]
    linear=[v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4 for v in values]
    return sum(v*w for v,w in zip(linear,(0.2126,0.7152,0.0722)))


def contrast(a,b):
    light,dark=sorted((luminance(a),luminance(b)),reverse=True)
    return (light+0.05)/(dark+0.05)


class ThemeChecks(unittest.TestCase):
    def test_viewer_text_roles_are_readable_on_all_three_surfaces(self):
        for mode,p in PALETTES.items():
            for ink in ('ink','ink-2','ink-3','accent','brass'):
                for surface in ('ground','surface','surface-2'):
                    with self.subTest(mode=mode,ink=ink,surface=surface):
                        self.assertGreaterEqual(contrast(p[ink],p[surface]),4.5)
            self.assertGreaterEqual(contrast(p['accent-ink'],p['accent']),4.5)

if __name__=='__main__':unittest.main()
