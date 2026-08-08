from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import AccountRegisterForm


User = get_user_model()


class AccountRegisterFormTests(TestCase):
	def test_register_form_saves_praktikan(self):
		form = AccountRegisterForm(
			data={
				'first_name': 'Budi',
				'last_name': 'Santoso',
				'email': 'budi@example.com',
				'role': 'PRAKTIKAN',
				'kelas': '2IA06',
				'identifier': '23123456',
				'password1': 'Secret12345!',
				'password2': 'Secret12345!',
			}
		)

		self.assertTrue(form.is_valid(), form.errors)

		user = form.save()

		self.assertEqual(user.role, User.Role.PRAKTIKAN)
		self.assertEqual(user.npm, '23123456')
		self.assertIsNone(user.assistant_id)
		self.assertTrue(user.check_password('Secret12345!'))

	def test_register_form_saves_asisten(self):
		form = AccountRegisterForm(
			data={
				'first_name': 'Siti',
				'last_name': 'Aulia',
				'email': 'siti@example.com',
				'role': 'ASISTEN',
				'identifier': 'AS-01',
				'password1': 'Secret12345!',
				'password2': 'Secret12345!',
			}
		)

		self.assertTrue(form.is_valid(), form.errors)

		user = form.save()

		self.assertEqual(user.role, User.Role.ASISTEN)
		self.assertEqual(user.assistant_id, 'AS-01')
		self.assertIsNone(user.npm)


class AccountRegisterViewTests(TestCase):
	def test_register_view_creates_user_and_redirects(self):
		response = self.client.post(
			reverse('authentication:register'),
			data={
				'first_name': 'Rina',
				'last_name': 'Putri',
				'email': 'rina@example.com',
				'role': 'PRAKTIKAN',
				'kelas': '2IA06',
				'identifier': '22112233',
				'password1': 'Secret12345!',
				'password2': 'Secret12345!',
			},
		)

		self.assertRedirects(response, reverse('authentication:login'))
		self.assertTrue(User.objects.filter(npm='22112233', role=User.Role.PRAKTIKAN).exists())
