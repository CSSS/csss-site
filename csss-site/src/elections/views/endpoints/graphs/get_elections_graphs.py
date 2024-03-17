import math

import matplotlib
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from csss.views.context_creation.create_main_context import create_main_context
from csss.views.pstdatetime import pstdatetime
from elections.models import NomineePosition, Election, VoterChoice
from elections.views.Constants import TAB_STRING

matplotlib.use("agg")
import matplotlib.pyplot as plt # noqa : E402
import numpy as np # noqa : E402


def get_elections_graphs(request):
    context = create_main_context(request, tab=TAB_STRING)
    elections = Election.objects.all().order_by('-date')
    overall_labels = []
    overall_numbers = []
    labels = []
    numbers = []
    if VoterChoice.objects.all().count() == 0:
        return HttpResponseRedirect(f"{settings.URL_ROOT}elections")
    today_date = pstdatetime.now()
    voter_choices = VoterChoice.objects.all()
    for election in elections:
        results_detected = voter_choices.filter(
            selection__nominee_speech__nominee__election_id=election.id
        ).count() > 0
        if election.end_date > today_date and results_detected:
            days = ""
            if election.date is not None:
                days += f"Start WeekDay: {election.date.strftime('%a')}\n"
            if election.end_date is not None and election.date is not None:
                days += f"{(election.end_date - election.date).days} Vote Days"
            election_name = "\n".join(election.human_friendly_name.split(":"))
            labels.append(f"{election_name}\n{days}")
            overall_labels.append(election_name)
            nominee_positions = NomineePosition.objects.all().filter(
                nominee_speech__nominee__election_id=election.id
            ).order_by('position_name')
            votes = 0
            indx = 0
            position = nominee_positions[indx].position_name
            while len(nominee_positions) > indx and nominee_positions[indx].position_name == position:
                votes += nominee_positions[indx].voterchoice_set.all().count()
                indx += 1
            numbers.append(votes)
            overall_numbers.append(votes)
    ticks = 0
    image_paths = []
    number_of_elections_per_graphs = 5
    image_paths.append(
        save_image(overall_labels, overall_numbers, "all_elections", "Number of Votes For Past Elections")
    )
    while ticks < len(labels):
        image_paths.append(
            save_image(
                labels[ticks:ticks+number_of_elections_per_graphs],
                numbers[ticks:ticks+number_of_elections_per_graphs],
                f"all_elections_{ticks}",
                f"Number of Votes for Past Elections "
                f"[{int(ticks/number_of_elections_per_graphs)+1}/"
                f"{(math.ceil(len(labels)/number_of_elections_per_graphs))}]"
            )
        )
        ticks += number_of_elections_per_graphs
    context['image_paths'] = image_paths
    return render(request, 'elections/elections_graph.html', context)


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
    officer_photo_path = f'elections/static/{static_folder}'
    full_path = f'{officer_photo_path}{pic_name}'
    if settings.ENVIRONMENT != "LOCALHOST":
        full_path = f"{settings.STATIC_ROOT}{static_folder}{pic_name}"
    image_path = f"{static_folder}{pic_name}"
    fig.savefig(full_path)
    plt.close(fig)
    return image_path
