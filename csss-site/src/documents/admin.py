# Register your models here.
from django.contrib import admin
from documents.models import Repo, Media, Picture, Video, Album, Event, SubCategory
from django.utils.translation import ugettext_lazy as _
import subprocess
import os
import datetime
import logging

# Register your models here.
logger = logging.getLogger('csss_site')

subcategories = []
path_to_file = ['documents_static', 'event-photos']


def go_through_youtube_links(album_path, event_name, album_date, album_name):
    file = open(album_path, "r")
    for link in file:
        link = link.rstrip()
        if link != '':
            event_key = Event.objects.get(event_name=event_name)
            album_key = Album.objects.get(date=album_date, name=album_name)

            retrieved_objects = Video.objects.all().filter(youtube_link=link)
            if len(retrieved_objects) == 0:
                video_instance = Video(youtube_link=link)
                video_instance.save()
            else:
                video_instance = retrieved_objects[0]

            retrieved_objects = Media.objects.all().filter(
                event=event_key,
                album_link=album_key,
                video=video_instance
            )
            if len(retrieved_objects) == 0:
                item_instance = Media(event=event_key, album_link=album_key, video=video_instance)
                item_instance.save()
            else:
                item_instance = retrieved_objects[0]

            item_sub_category = subcategories.copy()
            lvl = 0
            while len(item_sub_category) != 0:
                if len(
                    SubCategory.objects.all().filter(
                        media=item_instance,
                        level=lvl+1,
                        name=item_sub_category[0]
                    )
                ) == 0:
                    sub_category_instance = SubCategory(media=item_instance, level=lvl+1, name=item_sub_category[0])
                    sub_category_instance.save()
                item_sub_category.pop(0)
                lvl += 1
    file.close()


def iterate_through_media_for_specific_album(path_to_file, album_path, event_name, album_date, album_name):
    album_contents = os.listdir(album_path)
    for media in album_contents:
        path_to_file.append(media)
        if os.path.isdir(album_path+'/'+media):
            subcategories.append(media)
            iterate_through_media_for_specific_album(
                path_to_file,
                album_path+'/'+media,
                event_name,
                album_date,
                album_name
            )
            subcategories.pop()
        else:
            if media == 'videos.txt':
                go_through_youtube_links(album_path+'/'+media, event_name, album_date, album_name)
            elif media[0] != '.':
                file_location = album_path+'/'+media
                event_key = Event.objects.get(event_name=event_name)
                album_key = Album.objects.get(date=album_date, name=album_name)
                retrieved_objects = Picture.objects.all().filter(
                    absolute_file_path=file_location,
                    static_path="/".join(path_to_file)
                )
                if len(retrieved_objects) == 0:
                    picture_instance = Picture(absolute_file_path=file_location, static_path="/".join(path_to_file))
                    picture_instance.save()
                else:
                    picture_instance = retrieved_objects[0]

                retrieved_objects = Media.objects.all().filter(
                    name=media,
                    event=event_key,
                    album_link=album_key,
                    picture=picture_instance
                )
                if len(retrieved_objects) == 0:
                    item_instance = Media(name=media, event=event_key, album_link=album_key, picture=picture_instance)
                    item_instance.save()
                else:
                    item_instance = retrieved_objects[0]

                if album_key.album_thumbnail is None:
                    album_key.album_thumbnail = item_instance
                    album_key.save()

                item_sub_category = subcategories.copy()
                lvl = 0
                while len(item_sub_category) != 0:
                    if len(SubCategory.objects.all().filter(
                        media=item_instance,
                        level=lvl+1,
                        name=item_sub_category[0]
                        )
                    ) == 0:
                        sub_category_instance = SubCategory(
                            media=item_instance,
                            level=lvl+1,
                            name=item_sub_category[0]
                        )
                        sub_category_instance.save()
                    item_sub_category.pop(0)
                    lvl += 1
        path_to_file.pop()


def create_pictures_from_repo(repo_dir):
    folder_contents = os.listdir(repo_dir)
    for event_name in folder_contents:
        event_path = repo_dir+event_name
        if os.path.isdir(event_path) and event_name[0] != '.':
            path_to_file.append(event_name)
            event_name = event_name
            retrieved_objects = Event.objects.all().filter(event_name=event_name)
            if len(retrieved_objects) == 0:
                event = Event(event_name=event_name)
                event.save()
            else:
                event = retrieved_objects[0]
            albums = os.listdir(event_path)
            for album in albums:
                if album[0] != '.':
                    path_to_file.append(album)
                    album_date = ''
                    album_name = ''
                    if ' ' in album:  # there is a name for the album as well as a date
                        index_of_space = album.find(' ')
                        date_of_file = album[0:index_of_space]
                        if '-' in date_of_file:  # in this case,
                            # the album_name has the following format "YYYY-MM-DDD <album_name>"
                            first_dash = date_of_file.find('-')
                            second_dash = date_of_file.find('-', first_dash+1)
                            date_of_file = datetime.datetime(
                                int(date_of_file[0:first_dash]),
                                int(date_of_file[first_dash+1:second_dash]),
                                int(date_of_file[second_dash+1:])
                            )
                            album_name = album[index_of_space+1:]
                            album_date = date_of_file
                            album_name = album_name
                            if len(Album.objects.all().filter(date=date_of_file, name=album_name, event=event)) == 0:
                                album_instance = Album(date=date_of_file, name=album_name, event=event)
                                album_instance.save()
                        else:  # in this case, the album_name has the following format "YYYY <album_name>"
                            date_of_file = datetime.datetime(int(date_of_file), 1, 1)
                            album_name = album[index_of_space+1:]
                            album_date = date_of_file
                            album_name = album_name
                            if len(Album.objects.all().filter(date=date_of_file, name=album_name, event=event)) == 0:
                                album_instance = Album(date=date_of_file, name=album_name, event=event)
                                album_instance.save()
                    else:  # there is no name in the album folder
                        if '-' in album:  # in this case, the album_name has the following format "YYYY-MM-DDD"
                            first_dash = album.find('-')
                            second_dash = album.find('-', first_dash+1)
                            date_of_file = datetime.datetime(
                                int(album[0:first_dash]),
                                int(album[first_dash+1:second_dash]),
                                int(album[second_dash+1:])
                            )
                            album_date = date_of_file
                            if len(Album.objects.all().filter(date=date_of_file, event=event)) == 0:
                                album_instance = Album(date=date_of_file, event=event)
                                album_instance.save()
                        else:  # in this case, the album_name has the following format "YYYY"
                            date_of_file = datetime.datetime(int(album), 1, 1)
                            album_date = date_of_file
                            album_name = album_name
                            if len(Album.objects.all().filter(date=date_of_file, event=event)) == 0:
                                album_instance = Album(date=date_of_file, event=event)
                                album_instance.save()
                    album_path = "{0}/{1}".format(event_path, album)
                    # files = os.listdir(album_path)
                    iterate_through_media_for_specific_album(
                        path_to_file,
                        album_path,
                        event_name,
                        album_date,
                        album_name
                    )
                    path_to_file.pop()
            path_to_file.pop()


def clone_repos(repo_admin, request, queryset):
    for repo in queryset.all():
        logger.info(f"[documents/admin.py clone_repos()] doing a git pull inside of {repo.url}")
        commands = f'cd {repo.absolute_path}; git pull'
        exit_code, output = subprocess.getstatusoutput(commands)
        logger.info(f"[documents/admin.py clone_repos()] exit_code={exit_code} and output={output}")
        create_pictures_from_repo(repo.absolute_path)


clone_repos.short_description = _('Git Pull')


class RepoAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'url',
        'absolute_path',
        'static_path'
    )
    actions = [clone_repos]


class EventAdmin(admin.ModelAdmin):
    list_display = (
        'event_name',
    )


class AlbumAdmin(admin.ModelAdmin):
    list_display = (
        'event',
        'date',
        'name',
        'album_thumbnail'
    )


class MediaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'event',
        'album_link',
        'name',
        'picture',
        'video'
    )


class PictureAdmin(admin.ModelAdmin):
    list_display = (
        'absolute_file_path',
        'static_path'
    )


class VideoAdmin(admin.ModelAdmin):
    list_display = (
        'youtube_link',
    )


class SubCategoryAdmin(admin.ModelAdmin):
    list_display = (
        'media',
        'level',
        'name'
    )


admin.site.register(Repo, RepoAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(Media, MediaAdmin)
admin.site.register(Picture, PictureAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
