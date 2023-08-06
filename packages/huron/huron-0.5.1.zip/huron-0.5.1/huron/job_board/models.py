# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.template import loader

from huron.utils.models import RichTextField


class ContractType(models.Model):
    label = models.CharField(_(u'label'), max_length=255)
    slug = models.CharField(_(u'permalink'), max_length=255, unique=True)

    class Meta():
        verbose_name = _(u'contrat type')
        verbose_name_plural = _(u'contrat types')

    def __unicode__(self):
        return self.label


class Tag(models.Model):
    label = models.CharField(_(u'label'), max_length=255)
    slug = models.CharField(_(u'permalink'), max_length=255, unique=True)

    def __unicode__(self):
        return self.label


class Offer(models.Model):
    reference = models.CharField(_(u'job reference'), max_length=255,
                                 blank=True)
    title = models.CharField(_(u'job name'), max_length=255)
    slug = models.SlugField(_(u'permalink'))
    company_name = models.CharField(_(u'company name'), max_length=255)
    date_pub = models.DateField(_(u'publication date'), auto_now_add=True)
    date_last_edit = models.DateField(_(u'last edition date'), auto_now=True)
    date_unpub = models.DateField(_(u'end of publication date'))
    type = models.ForeignKey(ContractType)
    city = models.CharField(_(u'city'), max_length=255)
    zip = models.CharField(_(u'zip code'), max_length=25)
    short_desc = RichTextField(_(u'short description'), blank=True)
    job_desc = RichTextField(_(u'job description'))
    job_profile = RichTextField(_(u'job profil'))
    more_informations = RichTextField(_(u'more informations'), blank=True)
    begin_date = models.CharField(_(u'date of the beginning of the contract'),
                                  blank=True, max_length=255)
    filled = models.BooleanField(_(u'filled job'))
    send_to = models.EmailField(_(u'send application to'), blank=True)
    tags = models.ManyToManyField(Tag, null=True)

    def get_absolute_url(self):
        return '/emploi/%s' % self.slug

    def __unicode__(self):
        return self.title

    class Meta():
        get_latest_by = "date_last_edit"
        ordering = ['-date_last_edit']
        verbose_name = _(u'job offer')
        verbose_name_plural = _(u'job offers')


class Application(models.Model):
    last_name = models.CharField(_(u'name'), max_length=255)
    first_name = models.CharField(_(u'firstname'), max_length=255)
    email = models.EmailField(_(u'email'))
    date_apply = models.DateField(_(u'date of application'), auto_now_add=True)
    resume = models.FileField(_(u'resume'), upload_to='resume')
    cover_letter = models.FileField(_(u'cover letter'),
                                    upload_to='cover_letter', blank=True,
                                    null=True)
    text = RichTextField(_(u'introduction text'), blank=True)
    availability = models.CharField(_(u'availability'), blank=True,
                                    max_length=255)
    offer = models.ForeignKey(Offer)

    class Meta():
        verbose_name = _(u'application')
        verbose_name_plural = _(u'applications')
        unique_together = (("email", "offer"),)

    def __unicode__(self):
        return _(u'%(firstname)s %(name)s in'
                 ' answer to %(offer)s') % {'firstname': self.first_name,
                                            'name': self.last_name,
                                            'offer': self.offer}

    def save(self):
        # send email
        email_list = []
        current_site = Site.objects.get_current()
        site_url = current_site.domain
        if self.offer.send_to:
            email_list = [self.offer.send_to]
        else:
            email_list = [v for k,v in settings.MANAGERS]
        subject = _(u'New application for'
                    ' %(title)s') % {'title': self.offer.title}
        if self.offer.reference:
            subject = u'%s (%s)' % (subject, self.offer.reference)
        message = loader.render_to_string('job_board/application_mail.txt',
                                          {'application': self,
                                           'site_url': site_url})
        from_mail = [v for k,v in settings.MANAGERS]
        from_mail = from_mail[0]
        send_mail(subject, message, from_mail, email_list, fail_silently=False)
        super(Application, self).save()


class FreeApplication(models.Model):
    last_name = models.CharField(_(u'firstname'), max_length=255)
    first_name = models.CharField(_(u'lastname'), max_length=255)
    email = models.EmailField(_(u'email'))
    date_apply = models.DateField(_(u'date of application'), auto_now_add=True)
    resume = models.FileField(_(u'resume'), upload_to='resume')
    cover_letter = models.FileField(_(u'cover letter'),
                                    upload_to='cover_letter', blank=True,
                                    null=True)
    text = RichTextField(_(u'introduction text'), blank=True)
    availability = models.CharField(_(u'availability'), blank=True,
                                    max_length=255)

    class Meta():
        verbose_name = _(u'free application')
        verbose_name_plural = _(u'free applications')

    def __unicode__(self):
        return u'%s %s' % (self.first_name, self.last_name)

    def save(self):
        # send email
        current_site = Site.objects.get_current()
        site_url = current_site.domain
        email_list = [v for k,v in settings.MANAGERS]
        subject = _(u'New free application')
        message = loader.render_to_string('job_board/free_application_mail.txt',
                                          {'application': self,
                                           'site_url': site_url})
        from_mail = [v for k,v in settings.MANAGERS]
        from_mail = from_mail[0]
        send_mail(subject, message, from_mail, email_list, fail_silently=False)
        super(Application, self).save()
