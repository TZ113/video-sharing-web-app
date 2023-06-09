# Video-sharing-web-application
This is a video sharing web-application, built using django on the backend and javascript, HTML, CSS on the front. It's a simple and easy to use application, users can create accounts in this site and then upload videos, and people can watch these videos after accessing the site, like them, comment on them or add them to playlists etc, just like youtube. This is not a production-level work. I originally built it for the final project of my web development course (cs50W from Harvard via edX) and even after finishing the course, I kept practicing on it.

## Installing requirements
The settings file assumes that `rabbitmq-server` is running on `localhost` using default ports. More information is here:-

https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/rabbitmq.html#broker-rabbitmq

Additionally, some python requirements need to be satisfied. They can be installed using the following command:-

`pip3 install -r requirements.txt`
## Running the project
- The *facebook login* option requires ssl connection. To run the server with ssl:-
 
    `python3 manage.py runsslserver`
- *celery* is used for video conversion tasks. This command starts the celery worker:-

    `celery -A video_sharing_web_app worker -l INFO`
- *django-mailer* is used for sending confirmation emails for new user accounts, running database migration is necessary for it to work. Queued mails can be sent using the `python3 manage.py send_mail` command. Or as a better alternative, with the `python3 manage.py runmailer`, a long running process can be started that checks the database every 30  seconds and delivers the queued mails. And for scheduled automated delivery of messages a cron job file or equivalent can be configured. This link provides further information:-
    
    https://github.com/pinax/django-mailer/

The main page's url ends with `/home`, not `/`.
