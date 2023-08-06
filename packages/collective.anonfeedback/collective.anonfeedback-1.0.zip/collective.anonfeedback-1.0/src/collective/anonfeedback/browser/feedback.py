from App import config
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from glob import glob1
import os
import time

def feedback_dir():
    # XXX This needs to be configurable.
    clientdir = config.getConfiguration().clienthome
    vardir = os.path.realpath(os.path.join(clientdir, os.path.pardir))
    fbdir = os.path.join(vardir, 'feedback')
    if not os.path.exists(fbdir):
        os.mkdir(fbdir)
    return fbdir

class FeedbackForm(BrowserView):
    
    def handleform(self):
        form = self.request.form
        submit = form.get('submit', '')
        self.subject = form.get('subject', '').strip()
        self.feedback = form.get('feedback', '').strip()
        if submit:
            messages = IStatusMessage(self.request)
            if not self.subject or not self.feedback:
                messages.add(u'You must enter a subject and some feedback text.', type=u'error')
                return
            
            # Store feedback
            fbdir = feedback_dir()
            allfiles = glob1(fbdir, 'feedback.*.txt')
            if allfiles:
                maxnum = max([int(each.split('.')[1]) for each in allfiles])
            else:
                maxnum = 0
            
            while True:
                maxnum += 1
                filename = os.path.join(fbdir, 'feedback.%08i.txt' % maxnum)
                try:
                    # Create, but fail if file exists.
                    fd = os.open(filename, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                    break
                except OSError as e:
                    if e.errno == 17:
                        # The file already exists. Try again with a higher number.
                        continue                        
                    # Other error:
                    raise
    
            try:
                os.write(fd, """%s\n\n%s\n""" % (self.subject, self.feedback))
            finally:
                os.close(fd)
            
            # Clear fields:
            self.subject = ''
            self.feedback = ''
            messages.add(u'Your feedback has been submitted.', type=u'info')
            
            
class FeedbackView(BrowserView):
    
    def get_feedback(self):
        fbdir = feedback_dir()
        allfiles = sorted(glob1(fbdir, 'feedback.*.txt'), reverse=True)
        
        feedback = []
        for filename in allfiles:
            path = os.path.join(fbdir, filename)
            fb = open(path).read()
            subject, body = fb.split('\n\n', 1)
            body = body.split('\n')
            mtime = time.ctime(os.path.getmtime(path))
            feedback.append({'subject': subject, 'body': body, 'time': mtime})
            
        return feedback
        
        
