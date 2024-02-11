import matplotlib
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from csss.views.context_creation.create_main_context import create_main_context
from elections.models import NomineePosition, Election, VoterChoice
from elections.views.Constants import TAB_STRING

matplotlib.use("agg")
import matplotlib.pyplot as plt  # noqa
import numpy as np  # noqa


def get_election_graphs(request, slug):
    context = create_main_context(request, tab=TAB_STRING)
    position_names = [position.position_name for position in NomineePosition.objects.all().filter(
        nominee_speech__nominee__election__slug=slug,
    ).order_by('position_index')]
    positions_list = {}
    election_to_display = Election.objects.get(slug=slug)
    no_results = (
        VoterChoice.objects.all().filter(
            selection__nominee_speech__nominee__election_id=election_to_display.id
        ).count() == 0
    )
    if election_to_display.end_date is None and election_to_display.human_friendly_name != 'By-Election: 2015-11-04':
        # need to have the exception for By-Election: 2015-11-04 because I just couldn't find the end date for that
        # election unfortunately :-(
        return render(request, 'elections/graph.html', context)
    if no_results:
        return HttpResponseRedirect(f"{settings.URL_ROOT}elections/{slug}")
    for position_name in position_names:
        if position_name not in positions_list:
            positions_list[position_name] = []
            ordered_by_vote = {}
            human_nominee_positions = NomineePosition.objects.all().filter(
                position_name=position_name, nominee_speech__nominee__election__slug=slug
            )
            for human_nominee_position in human_nominee_positions:
                vote_count = human_nominee_position.voterchoice_set.all().count()
                if vote_count not in ordered_by_vote:
                    ordered_by_vote[vote_count] = [human_nominee_position]
                else:
                    ordered_by_vote[vote_count].append(human_nominee_position)
            order_count = list(ordered_by_vote.keys())
            order_count.sort(reverse=True)
            for vote_count in order_count:
                nominees = ordered_by_vote[vote_count]
                for nominee in nominees:
                    positions_list[position_name].append({
                        "nominee": nominee.nominee_speech.nominee.full_name, "count": vote_count})

    image_paths = []
    election_labels = []
    election_numbers = []
    for indx, position in enumerate(positions_list):
        position_specific_labels = []
        position_specific_numbers = []
        election_labels.append(position)
        election_numbers.append(0)
        for nominee_info in positions_list[position]:
            position_specific_labels.append(f"{nominee_info['nominee']}")
            position_specific_numbers.append(nominee_info['count'])
            election_labels.append(f"{nominee_info['nominee']}")
            election_numbers.append(nominee_info['count'])
        image_paths.append(
            save_image(
                position_specific_labels, position_specific_numbers,
                f"{election_to_display.slug}_{position}",
                f"Results for {election_to_display.human_friendly_name}: {position}"
            )
        )
    image_paths.insert(
        0,
        save_image(
            election_labels, election_numbers, election_to_display.slug,
            f"Result For {election_to_display.human_friendly_name}"
        ),
    )
    context['image_paths'] = image_paths
    context['election_obj'] = election_to_display
    return render(request, 'elections/graph.html', context)


def save_image(labels, numbers, image_name, title):
    plt.rcdefaults()
    fig, ax = plt.subplots()
    y_pos = np.arange(len(labels))
    for i, v in enumerate(numbers):
        ax.text(v, i + .25, f"{v}", color='blue', fontweight='bold')
    ax.barh(y_pos, numbers, align='center', color='green')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_title(title)
    fig.set_size_inches(18.5, 10.5)
    pic_name = f'{image_name}.png'
    static_folder = "elections_static/election_graphs/"
    if settings.ENVIRONMENT == "LOCALHOST":
        officer_photo_path = f'elections/static/{static_folder}'
        full_path = f'{officer_photo_path}{pic_name}'
        image_path = f"{static_folder}{pic_name}"
    else:
        full_path = f"{settings.STATIC_ROOT}{static_folder}{pic_name}"
        image_path = f"{static_folder}{pic_name}"
    fig.savefig(full_path)
    plt.close(fig)
    return image_path
