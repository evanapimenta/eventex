from django.core import mail
from django.test import TestCase
from eventex.subscriptions.forms import SubscriptionForm


class SubscribeTest(TestCase):

    def setUp(self):
        self.response = self.client.get('/inscricao/')


    def test_get(self):
        """Get /inscricao/ must return status code 200"""
        self.assertEqual(200, self.response.status_code)
        

    def test_template(self):
        """Must use subscriptions/subscription_form.html"""
        self.assertTemplateUsed(self.response, 'subscriptions/subscription_form.html')

    
    def test_html(self):
        """HTML must contain input tags"""
        self.assertContains(self.response, '<form')
        self.assertContains(self.response, '<input', 6)
        self.assertContains(self.response, 'type="text"', 3)
        self.assertContains(self.response, 'type="email"')
        self.assertContains(self.response, 'type="submit"')

    
    def test_csrf(self):
        """HTML must contain csrf"""
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    
    def test_has_form(self):
        """Context must have subscription form"""
        form = self.response.context['form']
        self.assertIsInstance(form, SubscriptionForm)

    def test_form_has_fields(self):
        form = self.response.context['form']
        self.assertSequenceEqual(['name', 'cpf', 'email', 'phone'], list(form.fields))


class SubscribePostTest(TestCase):
    def setUp(self):
        data = dict(name='Evana Pimenta', cpf='12345678901', email='evana@pimenta.com', phone='11-99999-9999')
        self.response = self.client.post('/inscricao/', data)
        
    def test_post(self):
        """Valid POST should redirect to /inscricao/"""
        self.assertEqual(302, self.response.status_code)

    def test_send_subscribe_email(self):
        self.assertEqual(1, len(mail.outbox))

    def test_subscription_email_subject(self):
        """E-mail subject and content of variable expect must be the same"""
        email = mail.outbox[0]
        expect = 'Confirmação de inscrição'

        self.assertEqual(expect, email.subject)

    def test_subscription_email_from(self):
        """Sender must be contato@eventex.com.br"""
        email = mail.outbox[0]
        expect = 'contato@eventex.com.br'

        self.assertEqual(expect, email.from_email)
    
    def test_subcription_email_to(self):
        """Receiver must be contato@eventex.com.br and evana@pimenta.com"""
        email = mail.outbox[0]
        expect = ['contato@eventex.com.br', 'evana@pimenta.com']

        self.assertEqual(expect, email.to)
    
    def test_subscription_email_body(self):
        email = mail.outbox[0]

        self.assertIn('Evana Pimenta', email.body)
        self.assertIn('12345678901', email.body)
        self.assertIn('evana@pimenta.com', email.body)
        self.assertIn('11-99999-9999', email.body)
        
class SubscribeInvalidPost(TestCase):
    def setUp(self):
        self.response = self.client.post('/inscricao/', {})

    def test_post(self):
        """Invalid POST should not redirect"""
        self.assertEqual(200, self.response.status_code)

    def test_template(self):
        """Invalid POST should render the subscription form"""
        self.assertTemplateUsed(self.response, 'subscriptions/subscription_form.html')
    
    def test_has_form(self):
        """Correct form must be in the context for template rendering"""
        form = self.response.context['form']
        self.assertIsInstance(form, SubscriptionForm)
    
    def test_form_has_errors(self):
        form = self.response.context['form']
        self.assertTrue(form.errors)

class SubscribeSuccessMessage(TestCase):
    def test_message(self):
        data = dict(name='Evana Pimenta', cpf='12345678901', email='evana@pimenta.com', phone='11-99999-9999')

        response = self.client.post('/inscricao/', data, follow=True)
        self.assertContains(response, 'Inscrição realizada com sucesso!')
