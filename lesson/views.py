from django import http
from sacado.settings import BBB_SERVEUR, BBB_SECRET, DEFAULT_FROM_EMAIL
import json
from xml.etree import ElementTree # pour lire le xml de la reponse de BBB
from subprocess import Popen,run
from django.utils import timezone
from django.shortcuts import render, redirect
from lesson.models import Event, ConnexionEleve
from lesson.forms import EventForm
from account.models import User, Student , Parent, Teacher
from school.models import School
import locale
locale.setlocale(locale.LC_TIME,'')
from datetime import datetime,timedelta
from django.template.loader import render_to_string
from django.http import JsonResponse 
#from django.core import serializers
from django.core.mail import send_mail
from general_fonctions import time_zone_user


import urllib.parse
import requests # debuggage, à enlever en developpement
from hashlib import sha1  # pour l'API de bbb
from lesson.models import *


def get_hours():
    return ["{:02d}:{:02d}".format(i//60,i%60) for i in range(8*60,20*60,15)]

def events_json(request):

    user =  request.user 
    events = user.events.all()
    event_list = []

    for event in events:
        # On récupère les dates dans le bon fuseau horaire
        event_start = event.start.astimezone(timezone.get_default_timezone())
        event_end = event.end.astimezone(timezone.get_default_timezone())
 
        event_list.append({
                    'id': event.id,
                    'start': event_start.strftime('%Y-%m-%d %H:%M:%S'),
                    'end': event_end.strftime('%Y-%m-%d %H:%M:%S'),
                    'title': event.title,
                    'color' : event.color,
                    })

    if len(event_list) == -1: 
        raise http.Http404
    else:
        return http.HttpResponse(json.dumps(event_list), content_type='application/json')
 


def calendar_show(request,id=0):
    user  = request.user
    form = EventForm(user, request.POST or None)
    hours = get_hours()

    context = { 'user_shown' : user , 'form' : form , 'hours' : hours ,   }  

    return render(request, "lesson/calendar_show.html" , context )
 


def create_event(request):

    user =  request.user  
    form = EventForm(user, request.POST or None)
    if form.is_valid():
        event = form.save(commit=False)
        event.user = request.user
        date_of_event = event.start 
        start_hour = request.POST.get("start_hour")
        tabs = start_hour.split(":")
        event.start = date_of_event + timedelta(hours=int(tabs[0]),minutes=int(tabs[1]))

        end_hour = request.POST.get("end_hour")
        tabe = end_hour.split(":")
 
        event.end = date_of_event + timedelta(hours=int(tabe[0]),minutes=int(tabe[1]))
        

        event.urlCreate=bbb_urlCreate(event)
        event.urlJoinProf=bbb_urlJoin(event,"MODERATOR", user.first_name+" "+user.last_name)
        event.urlIsMeetingRunning=bbb_urlIsMeetingRunning(event)
        event.save()  # pour avoir un id, necessaire pour les relations M2M
        users=form.cleaned_data.get("users")
        send_list = []
        ListeUrls=[]
        for eleve in users :
            event.users.add(eleve)
            conn=ConnexionEleve.objects.get(event=event,user=eleve)
            conn.urlJoinEleve=bbb_urlJoin(event,"VIEWER",eleve.first_name+" "+user.last_name)
            ListeUrls.append(conn.urlJoinEleve)
            conn.save()
            if eleve.email!=None : 
                send_list.append(eleve.email)    
        event.save()
        #-------------- envoi du mail au prof
        CorpsMessage="""Bonjour, 
Vous venez de créer une nouvelle leçon intitulée : {}.
Elle se déroulera le {} de {} à {}.
Voici le lien qui vous permettra d'accéder à la visio :
{}

Normalement, la visio sera créée automatiquement 3 minutes avant le rendez-vous. 
En cas de problème, ou pour la créer à la main, voici le lien :
{}  
""".format(str(event.title) ,str(date_of_event.strftime("%A %d/%m")),str(start_hour),str(end_hour),event.urlJoinProf,event.urlCreate)
        if len(users)==0 :
            CorpsMessage+="Cette leçon n'a pas d'élève, ce qui est curieux..."
        elif len(users)==1 :
            CorpsMessage+="Cette leçon est destinée à {} {}, et son lien d'accès est : \n{}\n"\
            .format(users[0].first_name.capitalize(), users[0].last_name.capitalize(),ListeUrls[0])
        else :
            CorpsMessage+="Voici la liste des élèves inscrits à cette leçon, et leurs liens d'accès respectifs : \n"
			
            for i,eleve in enumerate(users):
                CorpsMessage+=" - {} {} \n   {}\n".format(eleve.first_name.capitalize(),eleve.last_name.capitalize(),ListeUrls[i])
        CorpsMessage+="Cordialement,\nL'équipe de Sacado Académie"	  
        send_mail("Création d'une leçon",CorpsMessage,DEFAULT_FROM_EMAIL,[user.email])
        #---------------envoi du mail aux parents d'élèves et eventuellement aux eleves.
        for i,eleve in enumerate(users):
            student=Student.objects.get(user=eleve)
            dest=[p.user.email for p in student.students_parent.all()]
            if eleve.email != None : 
                dest.append(eleve.email) 
            send_mail("Programmation d'une leçon par visio","""
Bonjour,
Une leçon par visio a été programmée par {} {}, à destination de {} {}.
Elle aura lieu le {} de {} à {}.
Voici le lien d'accès à la visio :

{}

Merci de bien vouloir contacter l'enseignant à l'adresse {} en cas d'indisponibilité.

Très cordialement,

L'équipe Sacado Académie.
""".format(user.civilite,user.last_name.capitalize(),eleve.first_name.capitalize(),eleve.last_name.capitalize(), 
           str(date_of_event.strftime("%A %d/%m")),str(start_hour),str(end_hour),ListeUrls[i],user.email),DEFAULT_FROM_EMAIL,dest) 
    else:
        print(form.errors)
        
    return redirect('calendar_show' , 0)


 
 


def update_event(request,id):
    user = User.objects.get(pk=request.user.id)
    event = Event.objects.get(pk=id)
    form = EventForm(user, request.POST or None, instance = event)

    if form.is_valid():
        new_form = form.save(commit=False)
        start_hour = request.POST.get("start_hour")
        tabs = start_hour.split(":")
        new_form.start = new_form.start + timedelta(hours=int(tabs[0]),minutes=int(tabs[1]))

        #new_form.type_of_event = request.POST.get("type_of_event")

        end_hour = request.POST.get("end_hour")
        tabe = end_hour.split(":")
        new_form.end = new_form.end + timedelta(hours=int(tabe[0]),minutes=int(tabe[1]))
        new_form.user = user 
        new_form.urlCreate=bbb_urlCreate(new_form)
        new_form.urlJoinProf=bbb_urlJoin(new_form,"MODERATOR")
        new_form.urlJoinEleve=bbb_urlJoin(new_form,"VIEWER")
        new_form.save()

    else :
        print(form.errors)
        
    return redirect('calendar_show' , 0)


def shift_event(request):
 
    event_id = request.POST.get('event_id')
    new_start_event = request.POST.get('start_event')
    event = Event.objects.filter(pk=event_id).update(start=new_start_event)
 
    data = {} 
    return JsonResponse(data)

def show_event(request):
    event_id = request.POST.get('event_id')
    event = Event.objects.get(pk=event_id)   
    user = User.objects.get(pk=request.user.id) 
    form = EventForm(user, request.POST or None, instance = event) 

    same_day=   (event.end - event.start)<=timedelta(days=1)
 
    data = {}
     
    html = render_to_string('lesson/show.html',{ 'event' : event  , 'same_day': same_day ,  'form' : form  , 'hours' : get_hours()  , 'Prof' : request.user.user_type==user.TEACHER  })
    data['html'] = html       

    return JsonResponse(data)




def delete_event(request,id):
 
    event = Event.objects.get(pk=id)    
    event.delete()
    return redirect('calendar_show' , 0)



def add_students_to_my_lesson_group(request):
 
    user = request.user
    if request.method == "POST":
        students = request.POST.getlist('students')

        for s in students :
            print(s)
            user.teacher.students.add(s)
        return redirect('calendar_show' , 0)

    today   = time_zone_user(user)
    students = Student.objects.filter(user__school_id = 50,user__user_type=0, user__closure__lte= today  ).order_by("level__ranking", "user__last_name")
    
    context = { 'user' : user , 'students' : students , 'teacher' : user.teacher   }   
    return render(request, "lesson/add_students_to_my_lesson_group.html" , context )



def delete_student_to_my_lesson_group(request,id):
 
    user = request.user  
    s= Student.objects.get(user_id=id) 
    user.teacher.students.remove(s)
    return redirect('calendar_show' , 0)





def dashboard_parent(request):
 
    parent = Parent.objects.get(user=request.user)
    students = parent.students.order_by("user__first_name")
    index_tdb = False  # Permet l'affichage des tutos Youtube dans le dashboard
    today = time_zone_user(request.user)
    context = {'parent': parent, 'students': students, 'today' : today , 'index_tdb' : index_tdb, }
    template = 'lesson/dashboard_lesson_parent.html'
      
    return render(request, template , context )




def detail_student_lesson(request,id):
 
    user = request.user
    student = Student.objects.get(user_id=id)
    lessons = student.user.these_events.all()
    
    context = { 'user' : user , 'student' : student , 'lessons' : lessons   }   
    return render(request, "lesson/list_lessons.html" , context )





def ask_lesson(request,id):
 
    user = request.user
    student = Student.objects.get(user_id=id)
    teachers = Teacher.objects.filter(user__school_id=50,is_lesson=1).order_by("user__last_name")
    
    context = { 'user' : user , 'student' : student , 'teachers' : teachers   }   
    return render(request, "lesson/ask_lesson.html" , context )






def CalcMeetingID(event):
    """calcule du meetingID d'une leçon"""
    ID=event.user.last_name+" "+event.start.strftime("%d/%m %Hh%M")
    return sha1(ID.encode()).hexdigest()[:6]
        

def bbb_urlCreate(event):
    name=event.title
    meetingID=CalcMeetingID(event)
    welcome="Leçon par vidéo, enseignant"+( "e" if event.user.civilite=="Mme" else "")
    welcome+=" "+event.user.first_name+" "+event.user.last_name
    duration=str(max(30,int((event.end-event.start+timedelta(minutes=30)).total_seconds()//60))) #arrêt automatique de la session 30mn après la durée prévue de fin, au cas ou qq'un laisserait la session ouverte
    endWhenNoModerator="false" #la session se ferme lorsque le prof se deconnecte
    request="name={}&meetingID={}&welcome={}&duration={}&endWhenNoModerator={}"
    request=request.format(urllib.parse.quote(name),meetingID,urllib.parse.quote(welcome),duration,endWhenNoModerator)
    #print("create"+request+BBB_SECRET)

    hash=sha1(("create"+request+BBB_SECRET).encode()).hexdigest()
    request="https://"+BBB_SERVEUR+"/bigbluebutton/api/create?"+request+"&checksum="+hash
    
    body=r"""<?xml version="1.0" encoding="UTF-8"?><modules><module name="presentation"><document name="truc.pdf">JVBERi0xLjQKJdCX0LzQj9GeCiUlSW52b2NhdGlvbjogcGF0aC9ncyAtUC0gLWRTQUZFUiAtZENvbXBhdGliaWxpdHlMZXZlbD0xLjQgLXEgLVAtIC1kTk9QQVVTRSAtZEJBVENIIC1zREVWSUNFPXBkZndyaXRlIC1zc3Rkb3V0PT8gLXNPdXRwdXRGaWxlPT8gLVAtIC1kU0FGRVIgLWRDb21wYXRpYmlsaXR5TGV2ZWw9MS40ID8KNSAwIG9iago8PC9MZW5ndGggNiAwIFIvRmlsdGVyIC9GbGF0ZURlY29kZT4+CnN0cmVhbQp40ZorVDDQoDNUMABBKNGc0ZrQmxXQmAUANUkEZWVuZHN0cmVhbQplbmRvYmoKNiAwIG9iagoyMwplbmRvYmoKNCAwIG9iago8PC9UeXBlL1BhZ2UvTWVkaWFCb3ggWzAgMCA1OTUgODQyXQovUGFyZW50IDMgMCBSCi9SZXNvdXJjZXM8PC9Qcm9jU2V0Wy9QREZdCj4+Ci9Db250ZW50cyA1IDAgUgo+PgplbmRvYmoKMyAwIG9iago8PCAvVHlwZSAvUGFnZXMgL0tpZHMgWwo0IDAgUgpdIC9Db3VudCAxCj4+CmVuZG9iagoxIDAgb2JqCjw8L1R5cGUgL0NhdGFsb2cgL1BhZ2VzIDMgMCBSCi9NZXRhZGF0YSA3IDAgUgo+PgplbmRvYmoKNyAwIG9iago8PC9UeXBlL01ldGFkYXRhCi9TdWJ0eXBlL1hNTC9MZW5ndGggMTM0ND4+c3RyZWFtCjw/eHBhY2tldCBiZWdpbj0n0L/Cu9GXJyBpZD0nVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkJz8+Cjw/YWRvYmUteGFwLWZpbHRlcnMgZXNjPSJDUkxGIj8+Cjx4OnhtcG1ldGEgeG1sbnM6eD0nYWRvYmU6bnM6bWV0YS8nIHg6eG1wdGs9J1hNUCB0b29sa2l0IDIuOS4xLTEzLCBmcmFtZXdvcmsgMS42Jz4KPHJkZjpSREYgeG1sbnM6cmRmPSdodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjJyB4bWxuczppWD0naHR0cDovL25zLmFkb2JlLmNvbS9pWC8xLjAvJz4KPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9J3V1aWQ6MmQwM2IyY2YtOTgzNC0xMWY3LTAwMDAtNWE0NmUzMzE5Y2YzJyB4bWxuczpwZGY9J2h0dHA6Ly9ucy5hZG9iZS5jb20vcGRmLzEuMy8nIHBkZjpQcm9kdWNlcj0nR1BMIEdob3N0c2NyaXB0IDkuNTAnLz4KPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9J3V1aWQ6MmQwM2IyY2YtOTgzNC0xMWY3LTAwMDAtNWE0NmUzMzE5Y2YzJyB4bWxuczp4bXA9J2h0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8nPjx4bXA6TW9kaWZ5RGF0ZT4yMDIxLTEyLTE4VDE2OjMxOjUzKzAxOjAwPC94bXA6TW9kaWZ5RGF0ZT4KPHhtcDpDcmVhdGVEYXRlPjIwMjEtMTItMThUMTY6MzE6NTMrMDE6MDA8L3htcDpDcmVhdGVEYXRlPgo8eG1wOkNyZWF0b3JUb29sPlVua25vd25BcHBsaWNhdGlvbjwveG1wOkNyZWF0b3JUb29sPjwvcmRmOkRlc2NyaXB0aW9uPgo8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0ndXVpZDoyZDAzYjJjZi05ODM0LTExZjctMDAwMC01YTQ2ZTMzMTljZjMnIHhtbG5zOnhhcE1NPSdodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvbW0vJyB4YXBNTTpEb2N1bWVudElEPSd1dWlkOjJkMDNiMmNmLTk4MzQtMTFmNy0wMDAwLTVhNDZlMzMxOWNmMycvPgo8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0ndXVpZDoyZDAzYjJjZi05ODM0LTExZjctMDAwMC01YTQ2ZTMzMTljZjMnIHhtbG5zOmRjPSdodHRwOi8vcHVybC5vcmcvZGMvZWxlbWVudHMvMS4xLycgZGM6Zm9ybWF0PSdhcHBsaWNhdGlvbi9wZGYnPjxkYzp0aXRsZT48cmRmOkFsdD48cmRmOmxpIHhtbDpsYW5nPSd4LWRlZmF1bHQnPlVudGl0bGVkPC9yZGY6bGk+PC9yZGY6QWx0PjwvZGM6dGl0bGU+PC9yZGY6RGVzY3JpcHRpb24+CjwvcmRmOlJERj4KPC94OnhtcG1ldGE+CiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKPD94cGFja2V0IGVuZD0ndyc/PgplbmRzdHJlYW0KZW5kb2JqCjIgMCBvYmoKPDwvUHJvZHVjZXIoR1BMIEdob3N0c2NyaXB0IDkuNTApCi9DcmVhdGlvbkRhdGUoRDoyMDIxMTIxODE2MzE1MyswMScwMCcpCi9Nb2REYXRlKEQ6MjAyMTEyMTgxNjMxNTMrMDEnMDAnKT4+ZW5kb2JqCnhyZWYKMCA4CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDQ2NiAwMDAwMCBuIAowMDAwMDAxOTUwIDAwMDAwIG4gCjAwMDAwMDA0MDcgMDAwMDAgbiAKMDAwMDAwMDI5MyAwMDAwMCBuIAowMDAwMDAwMTgyIDAwMDAwIG4gCjAwMDAwMDAyNzUgMDAwMDAgbiAKMDAwMDAwMDUzMCAwMDAwMCBuIAp0cmFpbGVyCjw8IC9TaXplIDggL1Jvb3QgMSAwIFIgL0luZm8gMiAwIFIKL0lEIFs8NDRDNUY3MzcxNjdBMTA4MzQ5MDRBNUNGNkI4NkMyREI+PDQ0QzVGNzM3MTY3QTEwODM0OTA0QTVDRjZCODZDMkRCPl0KPj4Kc3RhcnR4cmVmCjIwNzMKJSVFT0YK"""+\
      r"""</document></module></modules>"""
    #print("\n\n----------- creation------------")
    #print(request)
    print("resultat : ")
    #print('curl -X POST "'+request+'" --header "Content-Type: application/xml" --data \''+body+"'")
    print('curl -X POST "'+request+'" --data \''+body+"'")
    
    #r=requests.post(request, data=bytes(body,'utf8')) # headers={'Content-Type':'application/xml'})
    #if r.status_code!=200 :
    #    print("Requête de création de visio a échoué, code=",r.status_code)
    #    return ""
    #print(r.content,"\n\n")
    #tree = ElementTree.fromstring(r.content)
    #returncode=tree[0].text
    #if returncode !="SUCCESS" :
    #    print("La requête a été traitée, mais elle a rendu {} : {}".format(returncode, tree[2].text))
    #    return ""
    #---------------
    # modification de crontab pour creer la reunion qq mn avant son début
    date_ouv=event.start-timedelta(minutes=3)
    date_ouv=date_ouv.strftime("%H:%M %m%d%y")
    print(date_ouv)
    com=open("/tmp/commande.txt","w")  #commande executée
    print("curl "+request, file=com)
    com.close()
    
    run(['at', date_ouv, "-f", "/tmp/commande.txt"])
    return request

def bbb_urlJoin(event,role,fullName):
    """lien pour ouvrir une visio. Role="MODERATOR" pour le prof,
    "VIEWER" pour les eleves"""

    #fullName=event.user.first_name+"_"+event.user.last_name
    meetingID=CalcMeetingID(event)
    request="fullName={}&meetingID={}&role={}"
    request=request.format(urllib.parse.quote(fullName),meetingID,role)
    hash=sha1(("join"+request+BBB_SECRET).encode()).hexdigest()
    request="https://"+BBB_SERVEUR+"/bigbluebutton/api/join?"+request+"&checksum="+hash
    #print("\n\n----------- connexion ------------")
    #print(request)
    #print("resultat : ")
    #print(requests.get(request).content,"\n\n")
    return request

def bbb_urlIsMeetingRunning(event):
	meetingID=CalcMeetingID(event)
	request="meetingID="+meetingID
	hash=sha1(("isMeetingRunning"+request+BBB_SECRET).encode()).hexdigest()
	request="https://"+BBB_SERVEUR+"/bigbluebutton/api/isMeetingRunning?"+request+"&checksum="+hash
	print("\n\n----------- connexion ------------")
	print(request)
	#print("resultat : ")
	#print(requests.get(request).content,"\n\n")
	return request
 
