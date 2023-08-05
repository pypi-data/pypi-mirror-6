:title: Project Gating

Project Gating
==============

Traditionally, many software development projects merge changes from
developers into the repository, and then identify regressions
resulting from those changes (perhaps by running a test suite with a
continuous integration system such as Jenkins), followed by more
patches to fix those bugs.  When the mainline of development is
broken, it can be very frustrating for developers and can cause lost
productivity, particularly so when the number of contributors or
contributions is large.

The process of gating attempts to prevent changes that introduce
regressions from being merged.  This keeps the mainline of development
open and working for all developers, and only when a change is
confirmed to work without disruption is it merged.

Many projects practice an informal method of gating where developers
with mainline commit access ensure that a test suite runs before
merging a change.  With more developers, more changes, and more
comprehensive test suites, that process does not scale very well, and
is not the best use of a developer's time.  Zuul can help automate
this process, with a particular emphasis on ensuring large numbers of
changes are tested correctly.

Zuul was designed to handle the workflow of the OpenStack project, but
can be used with any project.

A particular focus of Zuul is ensuring correctly ordered testing of
changes in parallel.  A gating system should always test each change
applied to the tip of the branch exactly as it is going to be merged.
A simple way to do that would be to test one change at a time, and
merge it only if it passes tests.  That works very well, but if
changes take a long time to test, developers may have to wait a long
time for their changes to make it into the repository.  With some
projects, it may take hours to test changes, and it is easy for
developers to create changes at a rate faster than they can be tested
and merged.

Zuul's DependentPipelineManager allows for parallel execution of test
jobs for gating while ensuring changes are tested correctly, exactly
as if they had been tested one at a time.  It does this by performing
speculative execution of test jobs; it assumes that all jobs will
succeed and tests them in parallel accordingly.  If they do succeed,
they can all be merged.  However, if one fails, then changes that were
expecting it to succeed are re-tested without the failed change.  In
the best case, as many changes as execution contexts are available may
be tested in parallel and merged at once.  In the worst case, changes
are tested one at a time (as each subsequent change fails, changes
behind it start again).  In practice, the OpenStack project observes
something closer to the best case.

For example, if a core developer approves five changes in rapid
succession::

  A, B, C, D, E

Zuul queues those changes in the order they were approved, and notes
that each subsequent change depends on the one ahead of it merging:

.. blockdiag::

  blockdiag foo {
    node_width = 40;
    span_width = 40;
    A <- B <- C <- D <- E;
  }

Zuul then starts immediately testing all of the changes in parallel.
But in the case of changes that depend on others, it instructs the
test system to include the changes ahead of it, with the assumption
they pass.  That means jobs testing change *B* include change *A* as
well::

  Jobs for A: merge change A, then test
  Jobs for B: merge changes A and B, then test
  Jobs for C: merge changes A, B and C, then test
  Jobs for D: merge changes A, B, C and D, then test
  Jobs for E: merge changes A, B, C, D and E, then test

Hence jobs triggered to tests A will only test A and ignore B, C, D:

.. blockdiag::

  blockdiag foo {
    node_width = 40;
    span_width = 40;
    master -> A -> B -> C -> D -> E;
    group jobs_for_A {
        label = "Merged changes for A";
        master -> A;
    }
    group ignored_to_test_A {
        label = "Ignored changes";
        color = "lightgray";
        B -> C -> D -> E;
    }
  }

The jobs for E would include the whole dependency chain: A, B, C, D, and E.
E will be tested assuming A, B, C, and D passed:

.. blockdiag::

  blockdiag foo {
    node_width = 40;
    span_width = 40;
    group jobs_for_E {
        label = "Merged changes for E";
        master -> A -> B -> C -> D -> E;
    }
  }

If changes *A* and *B* pass tests (green), and *C*, *D*, and *E* fail (red):

.. blockdiag::

  blockdiag foo {
    node_width = 40;
    span_width = 40;

    A [color = lightgreen];
    B [color = lightgreen];
    C [color = pink];
    D [color = pink];
    E [color = pink];

    master <- A <- B <- C <- D <- E;
  }

Zuul will merge change *A* followed by change *B*, leaving this queue:

.. blockdiag::

  blockdiag foo {
    node_width = 40;
    span_width = 40;

    C [color = pink];
    D [color = pink];
    E [color = pink];

    C <- D <- E;
  }

Since *D* was dependent on *C*, it is not clear whether *D*'s failure is the
result of a defect in *D* or *C*:

.. blockdiag::

  blockdiag foo {
    node_width = 40;
    span_width = 40;

    C [color = pink];
    D [label = "D\n?"];
    E [label = "E\n?"];

    C <- D <- E;
  }

Since *C* failed, Zuul will report its failure and drop *C* from the queue,
keeping D and E:

.. blockdiag::

  blockdiag foo {
    node_width = 40;
    span_width = 40;

    D [label = "D\n?"];
    E [label = "E\n?"];

    D <- E;
  }

This queue is the same as if two new changes had just arrived, so Zuul
starts the process again testing *D* against the tip of the branch, and
*E* against *D*:

.. blockdiag::

  blockdiag foo {
    node_width = 40;
    span_width = 40;
    master -> D -> E;
    group jobs_for_D {
        label = "Merged changes for D";
        master -> D;
    }
    group ignored_to_test_D {
        label = "Skip";
        color = "lightgray";
        E;
    }
  }

.. blockdiag::

  blockdiag foo {
    node_width = 40;
    span_width = 40;
    group jobs_for_E {
        label = "Merged changes for E";
        master -> D -> E;
    }
  }

