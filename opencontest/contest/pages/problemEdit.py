from html import escape

from django.http import HttpResponse

from contest.auth import admin_required
from contest.models.problem import Problem
from contest.pages.lib import Card, Page
from contest.pages.lib.htmllib import UIElement, h2, div, p, h, code_encode
from contest.pages.lib.page import Modal


class ProblemCard(UIElement):
    def __init__(self, prob: Problem):
        self.html = Card(prob.title, prob.description, link=f"/problems/{prob.id}/edit", delete=f"deleteProblem('{prob.id}')", cls=prob.id)


@admin_required
def listProblemsAdmin(request):
    problems = []
    Problem.forEach(lambda prob: problems.append(ProblemCard(prob)))
    return HttpResponse(Page(
        h2("Problems", cls="page-title"),
        div(cls="actions", contents=[
            h.button("+ Create Problem", cls="button create-problem", onclick="window.location='/problems/new'")
        ]),
        div(cls="problem-cards", contents=problems)
    ))


class TestDataCard(UIElement):
    def __init__(self, x):
        num, testData, samples = x
        isSample = num < samples
        title = f"Sample Data #{num}" if isSample else f"Judge Data #{num}"
        cls = "blue" if isSample else ""
        if testData.input == None: testData.input = "" 
        if testData.output == None: testData.output = "" 
        self.html = Card(title, div(cls="row", contents=[
            div(cls="col-6", contents=[
                p("Input:", cls="no-margin"),
                h.code(code_encode(testData.input))
            ]),
            div(cls="col-6", contents=[
                p("Output:", cls="no-margin"),
                h.code(code_encode(testData.output))
            ])
        ]), cls=cls, delete=f"deleteTestDataDialog({num})", edit=f"editTestDataDialog({num})")


@admin_required
def editProblem(request, *args, **kwargs):
    probId = kwargs.get('id')
    prob = Problem.get(probId)
    return HttpResponse(Page(
        h.input(type="hidden", id="prob-id", value=probId),
        h.input(type="hidden", id="pageId", value="Problem"),
        h2(prob.title, cls="page-title"),
        div(cls="actions", contents=[
            h.button("View Problem", cls="button", onclick=f"window.location='/problems/{probId}'"),
            h.button("+ Create Test Data", cls="button", onclick="createTestDataDialog()")
        ]),
        Card("Problem Details", div(cls="problem-details", contents=[
            h.form(cls="row", contents=[
                div(cls="form-group col-12", contents=[
                    h.label(**{"for": "problem-title", "contents":"Title"}),
                    h.input(cls="form-control", name="problem-title", id="problem-title", value=prob.title)
                ]),
                div(cls="form-group col-12", contents=[
                    h.label(**{"for": "problem-description", "contents":"Description"}),
                    h.textarea(cls="form-control", name="problem-description", id="problem-description", contents=escape(prob.description))
                ]),
                div(cls="form-group col-12 rich-text", contents=[
                    h.label(**{"for": "problem-statement", "contents":"Problem Statement"}),
                    h.textarea(cls="form-control", name="problem-statement", id="problem-statement", contents=escape(prob.statement))
                ]),
                div(cls="form-group col-12 rich-text", contents=[
                    h.label(**{"for": "problem-input", "contents":"Input Format"}),
                    h.textarea(cls="form-control", name="problem-input", id="problem-input", contents=escape(prob.input))
                ]),
                div(cls="form-group col-12 rich-text", contents=[
                    h.label(**{"for": "problem-output", "contents":"Output Format"}),
                    h.textarea(cls="form-control", name="problem-output", id="problem-output", contents=escape(prob.output))
                ]),
                div(cls="form-group col-12 rich-text", contents=[
                    h.label(**{"for": "problem-constraints", "contents":"Constraints"}),
                    h.textarea(cls="form-control", name="problem-constraints", id="problem-constraints", contents=escape(prob.constraints))
                ]),
                div(cls="form-group col-6", contents=[
                    h.label(**{"for": "problem-samples", "contents":"Number of Sample Cases"}),
                    h.input(cls="form-control", type="number", name="problem-samples", id="problem-samples", value=prob.samples)
                ]),
                div(cls="form-group col-6", contents=[
                    h.label(**{"for": "problem-timelimit", "contents":"Time Limit (secs)"}),
                    h.input(cls="form-control", type="number",name="problem-timelimit", id="problem-timelimit", value=escape(prob.timelimit))
                ]),
            ]),
            div(cls="align-right col-12", contents=[
                h.button("Save", cls="button", onclick="editProblem()")
            ])
          ])),
        Modal(
            "Create Test Data",
            div(
                h.h5("Input"),
                h.textarea(rows="5", cls="test-data-input col-12 monospace margin-bottom"),
                h.h5("Output"),
                h.textarea(rows="5", cls="test-data-output col-12 monospace")
            ),
            div(
                h.button("Cancel", **{"type":"button", "class": "button button-white", "data-dismiss": "modal"}),
                h.button("Add Test Data", **{"type":"button", "class": "button", "onclick": "createTestData()"})
            ),
            modalID="create-test-data"
        ),
        Modal(
            "Edit Test Data",
            div(
                h.h5("Input"),
                h.textarea(rows="5", cls="edit-test-input col-12 monospace margin-bottom"),
                h.h5("Output"),
                h.textarea(rows="5", cls="edit-test-output col-12 monospace"),
                h.p("ID", cls="current-test-data-id", hidden="")
            ),
            div(
                h.button("Cancel", **{"type":"button", "class": "button button-white", "data-dismiss": "modal"}),
                h.button("Save Changes", **{"type":"button", "class": "button", "onclick": "editTestData()"})
            ),
            modalID="edit-test-data"
        ),
        Modal(
            "Delete Confirmation",
            div(
                h.h2("Are you sure that you want to delete test case?", cls="delete-test-data-question"),
                h.p("ID", cls="delete-test-data-id", hidden="")
            ),
            div(
                h.button("No", **{"type":"button", "class": "button button-white", "data-dismiss": "modal"}),
                h.button("Yes", **{"type":"button", "class": "button", "onclick": "deleteTestData()"})
            ),
            modalID="delete-test-data"
        ),
        div(cls="test-data-cards", contents=list(map(TestDataCard, zip(range(prob.tests), prob.testData, [prob.samples] * prob.tests))))
    ))


@admin_required
def newProblem(request):
    return HttpResponse(Page(
        h.input(type="hidden", id="prob-id", value=""),
        h.input(type="hidden", id="pageId", value="Problem"),
        h2("New Problem", cls="page-title"),
        Card("Problem Details", div(cls="problem-details", contents=[
            h.form(cls="row", contents=[
                div(cls="form-group col-12", contents=[
                    h.label(**{"for": "problem-title", "contents":"Title"}),
                    h.input(cls="form-control", name="problem-title", id="problem-title", value="Title")
                ]),
                div(cls="form-group col-12", contents=[
                    h.label(**{"for": "problem-description", "contents":"Description"}),
                    h.textarea(cls="form-control", name="problem-description", id="problem-description", contents="Text for list of problems")
                ]),
                div(cls="form-group col-12 rich-text", contents=[
                    h.label(**{"for": "problem-statement", "contents":"Problem Statement"}),
                    h.textarea(cls="form-control", name="problem-statement", id="problem-statement", contents="Problem Statement")
                ]),
                div(cls="form-group col-12 rich-text", contents=[
                    h.label(**{"for": "problem-input", "contents":"Input Format"}),
                    h.textarea(cls="form-control", name="problem-input", id="problem-input", contents="Input Format")
                ]),
                div(cls="form-group col-12 rich-text", contents=[
                    h.label(**{"for": "problem-output", "contents":"Output Format"}),
                    h.textarea(cls="form-control", name="problem-output", id="problem-output", contents="Output Format")
                ]),
                div(cls="form-group col-12 rich-text", contents=[
                    h.label(**{"for": "problem-constraints", "contents":"Constraints"}),
                    h.textarea(cls="form-control", name="problem-constraints", id="problem-constraints", contents="Input Constraints")
                ]),
                div(cls="form-group col-12", contents=[
                    h.input(cls="form-control", type="hidden", name="problem-samples", id="problem-samples", value=0)
                ]),
               div(cls="form-group col-6", contents=[
                    h.label(**{"for": "problem-timelimit", "contents":"Problem Time Limit"}),
                    h.input(cls="form-control", type="number",name="problem-timelimit", id="problem-timelimit", value=Problem.default_timelimit)
                ]),
            ]),
            div(cls="align-right col-12", contents=[
                h.button("Save", cls="button", onclick="editProblem()")
            ])
          ]))
    ))
