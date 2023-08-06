# encoding: utf-8
from testcases import (
    TestServerTestCase,
    get_client
)
from django.core.management import call_command
from queryset_client.client import (
    FieldTypeError,
    ObjectDoesNotExist
)
from .utils import id_generator


class ModelTestCase(TestServerTestCase):

    def setUp(self):
        self.start_test_server()
        self.client = get_client()

    def tearDown(self):
        self.stop_test_server()

    def test_type1(self):
        value = 1
        message = self.client.message()
        message.id = value
        self.assertTrue(message.id == value)
        self.assertTrue(message._fields["id"] == value)

    def test_type2(self):
        value = 1
        message = self.client.message()
        try:
            message.subject = value
        except FieldTypeError:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_type3(self):
        value = 1
        message = get_client(strict_field=False).message()
        try:
            message.subject = value
        except FieldTypeError:
            self.assertTrue(False)
        else:
            self.assertTrue(True)

    def test_call1(self):
        subject = "subject call 1"
        body = "body call 1"
        message_obj = self.client.message(subject=subject, body=body)
        self.assertTrue(message_obj.subject == subject)
        self.assertTrue(message_obj.body == body)

    def test_call2(self):
        try:
            self.client.message(errorfield="oha yo! oha yo!")
        except FieldTypeError:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_save1(self):
        """ (new) """
        subject = "subject save 1"
        body = "body save 1"
        message = self.client.message(subject=subject, body=body)
        message.save()

        message_ = self.client.message.objects.get(id=message.id, subject=subject, body=body)
        self.assertTrue(message_.id == message.id)
        self.assertTrue(message_.subject == message.subject)
        self.assertTrue(message_.body == message.body)

    def test_save2(self):
        """ (update) """
        subject1 = "subject save 2"
        body1 = "body save 2"
        message = self.client.message(subject=subject1, body=body1)
        message.save()

        subject2 = "subject save 2 update"
        body2 = "body save 2 update"
        message.subject = subject2
        message.body = body2
        message.save()
        try:
            self.client.message.objects.get(id=message.id, subject=subject1, body=body1)
        except ObjectDoesNotExist:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

        try:
            message_ = self.client.message.objects.get(id=message.id, subject=subject2, body=body2)
        except ObjectDoesNotExist:
            self.assertTrue(False)
        else:
            self.assertTrue(True)
            self.assertTrue(message_.id == message.id)
            self.assertTrue(message_.subject == message.subject)
            self.assertTrue(message_.body == message.body)

    def test_save3(self):
        """ (update) for query_set """

        subject = id_generator()
        body = id_generator()

        fil = self.client.message.objects.filter(id__in=range(20, 33))

        for message in fil:
            message.subject = subject
            message.body = body
            message.save()

        for message in self.client.message.objects.filter(id__in=range(20, 33)):
            self.assertTrue(message.subject == subject)
            self.assertTrue(message.body == body)

    def test_object_save1(self):
        """ object save
        """
        for i in range(0, 12):
            message = self.client.message()
            message.subject = id_generator()
            message.body = id_generator()
            message.save()

            inbox = self.client.inbox()
            inbox.did = id_generator()
            inbox.save()

            inbox_message = self.client.inbox_message()
            inbox_message.message = message
            inbox_message.inbox = inbox
            inbox_message.save()  # TODO: save success

#    def test_save_rel1(self):
#        """ relation """
#        subject = ""
#        body = ""
#        message = self.client.inbox_message(subject=subject, body=body)
#        message.save()

    def test_save_many1(self):
        """ post """
        call_command('loaddata', 'base_data.json')
        for inbox_message in self.client.inbox_message.objects.all():
            inbox_message_many = self.client.inbox_message_many()
            inbox_message_many.inbox_message = inbox_message
            inbox_message_many.save()

    def test_save_many2(self):
        """ put """
        call_command('loaddata', 'base_data.json')
        for inbox_message_many in self.client.inbox_message_many.objects.all():
            inbox_message_many.save()

    def test_save_many3(self):
        """ add, remove, clear

        * Check resource_uri  (response, field)


        """
        call_command('loaddata', 'base_data.json')

        inbox_messages = []
        inbox_message_many = self.client.inbox_message_many.objects.get(id=2)
        count_orig = inbox_message_many.inbox_message.count()

        for i in range(0, 5):
            message = self.client.message()
            message.subject = id_generator()
            message.body = id_generator()
            message.save()

            inbox = self.client.inbox()
            inbox.did = id_generator()
            inbox.save()

            inbox_message = self.client.inbox_message()
            inbox_message.message = message
            inbox_message.inbox = inbox
            inbox_message.save()

            inbox_messages.append(inbox_message)
            inbox_message_many.inbox_message.add(inbox_message)
        inbox_message_many.save()
        self.assertTrue(
            inbox_message_many._response["inbox_message"] == inbox_message_many.model.inbox_message)

        inbox_all = inbox_message_many.inbox_message.all()
        for obj, obj_ in zip(inbox_all, inbox_message_many.inbox_message.filter()):
            self.assertTrue(obj.id == obj_.id)

        inbox_all_ = self.client.inbox_message.objects.filter(id__in=inbox_all._query["id__in"])
        self.assertTrue(len(inbox_all) == len(inbox_all_))
        for obj, obj_ in zip(inbox_all, inbox_all_):
            self.assertTrue(obj.id == obj_.id)

        ids = inbox_all._query["id__in"]
        inbox_message_many = self.client.inbox_message_many.objects.get(id=2)
        num = inbox_message_many.inbox_message.filter(id=ids[0]).count()
        self.assertTrue(num == 1)

        # remove
        inbox_message_many.inbox_message.remove(*inbox_messages)
        self.assertTrue(count_orig == inbox_message_many.inbox_message.count())
        inbox_message_many.save()
        self.assertTrue(count_orig == inbox_message_many.inbox_message.count())

        # clear  TODO: Issue #??
#        inbox_message_many.inbox_message.clear()
#        self.assertTrue(0 != inbox_message_many.inbox_message.count())
#        inbox_message_many.save()
#        self.assertTrue(0 == inbox_message_many.inbox_message.count())

        inbox_message_many.save()


    def test_delete1(self):
        subject = "subject delete 1"
        body = "body delete 1"
        message = self.client.message(subject=subject, body=body)
        message.save()

        message_ = self.client.message.objects.get(id=message.id, subject=subject, body=body)
        self.assertTrue(message_.id == message.id)
        self.assertTrue(message_.subject == message.subject)
        self.assertTrue(message_.body == message.body)

        message.delete()
        try:
            message.id
        except AttributeError:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

        try:
            message_.delete()
        except Exception:
            self.assertTrue(True)
        else:
            self.assertTrue(False)
        try:
            message.id
        except AttributeError:
            self.assertTrue(True)
        else:
            self.assertTrue(False)
