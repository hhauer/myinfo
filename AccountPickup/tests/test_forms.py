__author__ = "Justin McClure"
from django.test import TestCase
from AccountPickup.forms import OdinNameForm, EmailAliasForm


class OdinNameFormTestCase(TestCase):
    choices = ["Name 1 - Test1",
               "Name 2 - Test2", ]

    def test_good_init(self):
        # Test successful init without data
        form = OdinNameForm(enumerate(self.choices))
        self.assertEqual(form.fields['name'].label, "Odin Username")
        self.assertEqual([c for c in form.fields['name'].choices], [(0, "Name 1 - Test1"), (1, "Name 2 - Test2")])

        # Test init with data
        form = OdinNameForm(enumerate(self.choices), {"name": 1})
        self.assertEqual(form.fields['name'].label, "Odin Username")
        self.assertEqual([c for c in form.fields['name'].choices], [(0, "Name 1 - Test1"), (1, "Name 2 - Test2")])
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data, {"name": "1"})

    def test_bad_init(self):
        # Test init with no choices
        self.assertRaises(TypeError, OdinNameForm)
        # Test init with non-iterable choices
        self.assertRaises(TypeError, OdinNameForm, 42)


class EmailAliasFormTestCase(TestCase):
    choices = ["Name 1 - Test1",
               "Name 2 - Test2", ]

    def test_good_init(self):
        # Test successful init without data
        form = EmailAliasForm(enumerate(self.choices))
        self.assertEqual(form.fields["alias"].label, "Email Alias")
        self.assertEqual([c for c in form.fields["alias"].choices], [(0, "Name 1 - Test1"), (1, "Name 2 - Test2")])

        # Test init with data
        form = EmailAliasForm(enumerate(self.choices), {"alias": 1})
        self.assertEqual(form.fields["alias"].label, "Email Alias")
        self.assertEqual([c for c in form.fields["alias"].choices], [(0, "Name 1 - Test1"), (1, "Name 2 - Test2")])
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data, {"alias": "1"})

    def test_bad_init(self):
        # Test init with no choices
        self.assertRaises(TypeError, EmailAliasForm)
        # Test init with non-iterable choices
        self.assertRaises(TypeError, EmailAliasForm, 42)