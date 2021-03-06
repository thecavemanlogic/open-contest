# unique comment identifer

import time

from django.http import HttpResponse

from contest.auth import admin_required
from contest.models.contest import Contest
from contest.models.problem import Problem
from contest.pages.lib import Card, Page
from contest.pages.lib.htmllib import UIElement, div, h, h2
from contest.pages.lib.page import Modal


class ContestCard(UIElement):
    def __init__(self, contest: Contest):
        self.html = Card(contest.name, 
            div(
                h.span(contest.start, cls='time-format', data_timestamp=contest.start),
                " - ",
                h.span(contest.end, cls='time-format', data_timestamp=contest.end)
            ),
            link=f"/contests/{contest.id}",
            delete=f"deleteContest('{contest.id}')",
            cls=contest.id
        )


@admin_required
def listContests(request):
    contests = [*map(ContestCard, Contest.all())]
    return HttpResponse(Page(
        h2("Contests", cls="page-title"),
        div(cls="actions", contents=[
            h.button("+ Create Contest", cls="button create-contest", onclick="window.location='/contests/new'")
        ]),
        div(cls="contest-cards", contents=contests)
    ))


class ProblemCard(UIElement):
    def __init__(self, prob: Problem):
        self.html = Card(prob.title, prob.description, link=f"/problems/{prob.id}/edit", delete=f"deleteContestProblem('{prob.id}')", cls=prob.id)


@admin_required
def editContest(request, *args, **kwargs):
    id = kwargs.get('id')
    contest = Contest.get(id)

    title = "New Contest"
    chooseProblem = ""
    existingProblems = []
    start = time.time() * 1000
    end = (time.time() + 3600) * 1000
    scoreboardOff = end
    displayFullname = False
    showProblInfoBlocks = ""

    showProblInfoBlocks_option = [
        h.option("On", value="On"),
        h.option("Off", value="Off")
    ]
    
    tieBreaker = False
    if contest:
        title = contest.name
        start = contest.start
        end = contest.end
        scoreboardOff = contest.scoreboardOff   
        
        displayFullname = contest.displayFullname

        showProblInfoBlocks = contest.showProblInfoBlocks
        if showProblInfoBlocks == "Off":
            showProblInfoBlocks_option = [h.option("Off", value="Off"), h.option("On", value="On")]
        tieBreaker = contest.tieBreaker        

        chooseProblem = div(cls="actions", contents=[
            h.button("+ Choose Problem", cls="button", onclick="chooseProblemDialog()")
        ])

        problems = [ProblemCard(prob) for prob in contest.problems]
        problemOptions = [h.option(prob.title, value=prob.id) for prob in Problem.all() if prob not in contest.problems]

        existingProblems = [
            Modal(
                "Choose Problem",
                h.select(cls="form-control problem-choice", contents=[
                    h.option("-"),
                    *problemOptions
                ]),
                div(
                    h.button("Cancel", **{"type":"button", "class": "button button-white", "data-dismiss": "modal"}),
                    h.button("Add Problem", **{"type":"button", "class": "button", "onclick": "chooseProblem()"})
                )
            ),
            div(cls="problem-cards", contents=problems)
        ]
    
    return HttpResponse(Page(
        h.input(type="hidden", id="contest-id", value=id),
        h.input(type="hidden", id="pageId", value="Contest"),
        h2(title, cls="page-title"),
        chooseProblem,
        Card("Contest Details", div(cls="contest-details", contents=[
            h.form(cls="row", contents=[
                div(cls="form-group col-12", contents=[
                    h.label(**{"for": "contest-name", "contents":"Name"}),
                    h.input(cls="form-control", name="contest-name", id="contest-name", value=title)
                ]),
                h.input(type="hidden", id="start", value=start),
                div(cls="form-group col-6", contents=[
                    h.label(**{"for": "contest-start-date", "contents":"Start Date"}),
                    h.input(cls="form-control", name="contest-start-date", id="contest-start-date", type="date")
                ]),
                div(cls="form-group col-6", contents=[
                    h.label(**{"for": "contest-start-time", "contents":"Start Time"}),
                    h.input(cls="form-control", name="contest-start-time", id="contest-start-time", type="time")
                ]),
                h.input(type="hidden", id="end", value=end),
                div(cls="form-group col-6", contents=[
                    h.label(**{"for": "contest-end-date", "contents":"End Date"}),
                    h.input(cls="form-control", name="contest-end-date", id="contest-end-date", type="date")
                ]),
                div(cls="form-group col-6", contents=[
                    h.label(**{"for": "contest-end-time", "contents":"End Time"}),
                    h.input(cls="form-control", name="contest-end-time", id="contest-end-time", type="time")
                ]),
                h.input(type="hidden", id="showProblInfoBlocks", value=showProblInfoBlocks),                
                div(cls="form-group col-6", contents=[
                    h.label(**{"for": "show-problem-info-blocks", "contents":"Show Problem Info Blocks"}),
                    h.select(cls="form-control custom-select", name="show-problem-info-blocks", id="show-problem-info-blocks", contents=showProblInfoBlocks_option)
                ]),                               
                h.input(type="hidden", id="scoreboardOff", value=scoreboardOff),
                div(cls="form-group col-6", contents=[
                    h.label(**{"for": "scoreboard-off-time", "contents":"Turn Scoreboard Off Time"}),
                    h.input(cls="form-control", name="scoreboard-off-time", id="scoreboard-off-time", type="time")
                ]),
                div(cls="form-group col-6", contents=[
                    h.label(**{"for": "scoreboard-tie-breaker", "contents":"Sample Data Breaks Ties"}),
                    h.select(cls="form-control", name="scoreboard-tie-breaker", id="scoreboard-tie-breaker", contents=[
                        *[h.option(text, value=val, selected="selected") if tieBreaker == val else
                          h.option(text, value=val) for text, val in zip(("On", "Off"), (True, False))]
                    ])
                ]),

                # Option to display a users' fullname
                h.input(type="hidden", id="displayFullname", value=displayFullname),                
                div(cls="form-group col-6", contents=[
                    h.label(**{"for": "contest-display-fullname", "contents":"Show Full Name"}),
                    h.select(cls="form-control", name="contest-display-fullname", id="contest-display-fullname", contents=[
                        *[h.option(text, value=val, selected="selected") if displayFullname == val else
                          h.option(text, value=val) for text, val in zip(("On", "Off"), (True, False))]
                    ])
                ]),
            ]),
            div(cls="align-right col-12", contents=[
                h.button("Save", cls="button", onclick="editContest()")
            ])
        ])),
        *existingProblems
    ))
