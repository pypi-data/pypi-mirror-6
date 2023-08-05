from django.core.management.base import NoArgsCommand
from django.contrib.sessions.models import Session

from ... import backend, utils


class Command(NoArgsCommand):
    help = 'copy django orm sessions to redis'

    def handle_noargs(self, *args, **kwargs):
        now = utils.timezone.now()

        sessions = Session.objects.filter(expire_date__gt=now)
        count = sessions.count()
        counter = 1

        self.stdout.write('sessions to copy %d\n' % count)

        for session in sessions:
            self.stdout.write('processing %d of %d\n' % (counter, count))

            expire_in = session.expire_date - now
            expire_in = expire_in.seconds + expire_in.days * 86400

            backend.delete(session.session_key)

            backend.save(
                session.session_key,
                expire_in,
                session.session_data,
                False
            )

            counter += 1
