:- pmo(pmo, [event/1, activity/1, case/1, object/1, timestamp/1, resource/1]).

% Mutual exclusivity of classes - ommitted

% resources are objects
object(R) :- resource(R).

% has_object is a subproperty of has_resource.
has_object(X, O) :- has_resource(X, O).

% range constraints
case(C) :- has_case(X, C).
timestamp(T) :- has_recorded_time(X, T).
object(O) :- has_object(X, O).
resource(R) :- has_resource(X, R).
activity(A) :- has_activity(X, A).


% every event has a unique recorded time
has_unique_recorded_time(E) :-
    findall(T, has_recorded_time(E, T), Times),
    length(Times, L), L =< 1.

has_unique_recorded_time(E) :- event(E).

% Timepoint ordering is a subset of general ordering
time_before(T1, T2) :- 
    before(T1, T2).

% before inequality
dif(T1,T2) :- time_before(T1,T2).

% Transitivity of time_before, avoiding loops by ensuring T1 and T3 are different and adding cut
time_before(T1, T3) :- 
    before(T1, T2), 
    T1 \= T3, 
    time_before(T2, T3).

% --- Process Mining Reasoning ---

% Definition of event precedes
event_precedes(E1, E2) :-
    event(E1),
    event(E2),
    E1 \= E2,
    has_recorded_time(E1, T1),
    has_recorded_time(E2, T2),
    time_before(T1, T2).

% Definition of directly follows
directly_follows(E1, E2, C) :-
    event_precedes(E1, E2),
    has_case(E1, C),
    has_case(E2, C),
    \+ (event(E3), has_case(E3, C), event_precedes(E1, E3), event_precedes(E3, E2)).

% definition of hand-off
hand_off(E1, E2, C) :-
    directly_follows(E1, E2, C),
    has_resource(E1, R1),
    has_object(E2, R2),
    \+ (R1 = R2).

% definition of ping-pong
ping_pong(C) :-
    hand_off(E1, E2, C),
    hand_off(E3, E4, C),
    \+ (E1 = E3),
    \+ (E2 = E4).

% Individuals
resource(user_1).
resource(user_2).
resource(user_0).
event(event_5).
event(event_3).
event(event_1).
event(event_6).
event(event_7).
event(event_0).
event(event_9).
event(event_2).
event(event_4).
event(event_8).
case(case_2).
case(case_1).
case(case_0).
activity(activity_C).
activity(activity_A).
activity(activity_D).
activity(activity_B).
dif(event_1, event_2).
dif(event_0, event_9).
dif(event_7, event_6).
has_resource(event_5, user_0).
has_activity(event_4, activity_B).
dif(event_0, event_8).
dif(event_2, event_8).
dif(event_1, event_8).
dif(event_3, event_4).
has_case(event_5, case_1).
has_activity(event_9, activity_D).
dif(user_0, user_1).
has_activity(event_1, activity_A).
has_activity(event_2, activity_C).
dif(event_0, event_4).
dif(event_2, event_4).
dif(event_3, event_6).
has_resource(event_6, user_1).
dif(event_1, event_4).
has_activity(event_0, activity_A).
dif(event_9, event_4).
has_case(event_8, case_2).
dif(event_5, event_4).
has_case(event_1, case_0).
dif(event_8, event_4).
dif(event_0, event_6).
dif(event_1, event_6).
dif(activity_A, activity_D).
dif(case_1, case_0).
dif(event_9, event_6).
dif(event_5, event_6).
has_case(event_3, case_1).
dif(event_8, event_6).
dif(event_3, event_2).
dif(event_9, event_5).
has_case(event_6, case_2).
dif(case_2, case_1).
dif(event_3, event_1).
has_resource(event_0, user_1).
dif(activity_D, activity_C).
dif(user_2, user_0).
dif(event_2, event_9).
dif(event_3, event_7).
has_resource(event_1, user_1).
has_case(event_2, case_0).
dif(event_1, event_9).
has_resource(event_2, user_1).
has_resource(event_9, user_1).
dif(user_2, user_1).
dif(event_0, event_1).
dif(event_8, event_9).
dif(event_0, event_7).
has_activity(event_7, activity_B).
dif(event_2, event_7).
dif(event_0, event_3).
dif(event_1, event_7).
dif(event_9, event_7).
dif(event_5, event_7).
dif(event_8, event_7).
has_activity(event_8, activity_C).
has_resource(event_8, user_2).
dif(activity_B, activity_D).
has_activity(event_3, activity_A).
has_case(event_4, case_1).
has_resource(event_4, user_0).
has_case(event_9, case_2).
dif(event_3, event_5).
has_activity(event_5, activity_C).
has_resource(event_7, user_1).
dif(event_2, event_6).
dif(activity_B, activity_C).
dif(event_0, event_5).
dif(activity_B, activity_A).
dif(event_2, event_5).
dif(event_1, event_5).
has_case(event_7, case_2).
dif(event_7, event_4).
dif(event_3, event_9).
dif(case_2, case_0).
dif(event_6, event_4).
has_case(event_0, case_0).
dif(event_8, event_5).
dif(activity_A, activity_C).
has_resource(event_3, user_1).
dif(event_0, event_2).
has_activity(event_6, activity_A).
dif(event_3, event_8).
timepoint(ts_0).
timepoint(ts_1).
timepoint(ts_2).
timepoint(ts_3).
timepoint(ts_4).
timepoint(ts_5).
timepoint(ts_6).
has_recorded_time(event_2, ts_3).
has_recorded_time(event_5, ts_5).
has_recorded_time(event_3, ts_4).
has_recorded_time(event_4, ts_4).
has_recorded_time(event_6, ts_0).
has_recorded_time(event_0, ts_0).
has_recorded_time(event_9, ts_6).
has_recorded_time(event_7, ts_1).
has_recorded_time(event_8, ts_2).
has_recorded_time(event_1, ts_2).
before(ts_0,ts_1).
before(ts_1,ts_2).
before(ts_2,ts_3).
before(ts_3,ts_4).
before(ts_4,ts_5).
before(ts_5,ts_6).