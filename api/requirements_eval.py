from typing import Dict, List, Tuple, Any, Set
from .requirements import ALIASES, DEGREE_REQUIREMENTS, MAJOR_REQUIREMENTS

#removes extra whitespaces
def _squash_spaces(s: str) -> str:
    return " ".join(s.split())

#
def normalize_code(code: str) -> str:
    """
    Upper case, squeeze spaces, then apply alias mapping.
    Example: 'Comp Sci/ECE 354' -> 'COMP SCI 354'
    """
    if not code:
        return ""
    upper = _squash_spaces(code.upper().strip())
    return ALIASES.get(upper, upper)

def build_user_catalog(planned_courses: List[Dict[str, Any]]) -> Tuple[Set[str], Dict[str, float]]:
    """
    Take the user's plannedCourses (list of dicts with 'code' and 'credits')
    and create:
      user_codes: set of normalized course codes for quick checks
      user_credits: dictionary mapping normalized code -> credits (float)

    Example:
      Input: [{"code": "COMP SCI/E C E 354", "credits": 3}]
      Output:
        user_codes = {"COMP SCI 354"}
        user_credits = {"COMP SCI 354": 3.0}
    """
    user_codes = set() #Set of strings
    user_credits: Dict[str, float] = {} #dictionary with [string:float]
    for c in planned_courses:
        norm = normalize_code(str(c["code"]))
        user_codes.add(norm)
        # prefer numeric, fallback 0
        credits_raw = c.get("credits", 0)
        try:
            cr = float(credits_raw) if credits_raw is not None else 0.0
        except (ValueError, TypeError):
            cr = 0.0

        user_credits[norm] = cr
    return user_codes, user_credits

# ---------- Section evaluators ----------

def eval_all_of(section: Dict[str, Any], user_codes: Set[str], user_credits: Dict[str, float]) -> Dict[str, Any]:
    """
    Evaluate a requirement section where the student must complete ALL listed courses.
    Parameters
    section : dictionary
        A dictionary describing this section of the requirements.  
        Expected keys:
        "items":
            [
                {"code": "COMP SCI 300", "credits": 3},
                {"code": "COMP SCI 400", "credits": 3},
                ...
            ]
    user_codes : set of str
        A set containing all normalized course codes the student has planned or completed.
        Example:
            {"COMP SCI 300", "COMP SCI 252", "MATH 221"}
        This comes from `build_user_catalog()` and is used for quick membership checks.

    user_credits : dict
        A dictionary mapping each normalized course code to the number of credits the student has earned or planned.
        Example:
            {
                "COMP SCI 300": 3.0,
                "COMP SCI 252": 3.0,
                "MATH 221": 5.0
            }
        This also comes from `build_user_catalog()` and is based on user input in the database.

    Returns
    dict
        {
            "status": str,              # "complete", "in_progress", or "missing"
            "taken": list[dict],        # courses from section that the student has
            "missing": list[dict],      # courses from section that the student does not have
            "credited_codes": list[str],# set of codes that count toward the major credits (for deduplication later)
            "credits_earned": float     # total credits earned from courses in this section
        }
    """
    
    # List of courses in this section that the student has taken or planned
    taken = []

    # List of courses in this section that the student is still missing
    missing = []

    # A set of course codes that should be credited toward the major total (avoids double counting later)
    credited_codes = set()

    # Loop through every course in the section's items list
    for item in section.get("items", []):
        # Normalize the course code for consistency (uppercasing, removing extra spaces, alias mapping)
        code = normalize_code(item["code"])

        # Check if the student has this course in their taken/planned list
        if code in user_codes:
            # Add it to taken list
            taken.append({"code": code, "credits": item.get("credits")})
            # Mark this code as credit-able for the major
            credited_codes.add(code)
        else:
            # The student does not have this course yet → add to missing list
            missing.append({"code": code, "credits": item.get("credits")})

    # Determine the overall status of this section:
    # - "complete" if no courses are missing
    # - "in_progress" if some courses are taken but not all
    # - "missing" if none of the courses are taken
    if not missing:
        status = "complete"
    elif taken:
        status = "in_progress"
    else:
        status = "missing"

    # Calculate total credits earned for the taken courses in this section
    credits_earned = 0
    for t in taken:
        code = t["code"]
        # Try to get credits from the user's data (most accurate)
        if code in user_credits:
            credits = user_credits[code]
        else:
            # Fall back to the requirement's course credit value
            credits = t.get("credits", 0)
            if credits is None:
                credits = 0
        credits_earned += credits

    # Return the result as a dictionary
    return {
        "status": status,
        "taken": taken,
        "missing": missing,
        "credited_codes": list(credited_codes),
        "credits_earned": credits_earned,
    }

def _score_all_of(option_items: List[Dict[str, Any]], user_codes: Set[str]) -> Tuple[int, List[Dict[str, Any]], List[Dict[str, Any]], Set[str]]:
    """
    Helper function for ONE_OF sections:
    Given a list of course items, check how many the user has taken.

    Parameters
    option_items : list[dict]
        List of course dictionaries, each with:
        - "code": course identifier
        - "credits": default credit value

    user_codes : set[str]
        Set of all normalized course codes the user has completed/planned.

    Returns
    tuple:
        (
            match_count: int         # how many of these courses the user has taken
            taken_list: list[dict]   # courses from option_items that the user has taken
            missing_list: list[dict] # courses from option_items the user does NOT have
            credited_codes: set[str] # codes that should count for credit
        )
    """
    taken = []       # List of courses the user has from option_items
    missing = []     # List of courses the user is missing from option_items
    credited = set() # Set of codes that should be credited toward the requirement

    for it in option_items:
        code = normalize_code(it["code"])  # Clean up formatting/case for matching
        if code in user_codes:
            taken.append({"code": code, "credits": it.get("credits")})
            credited.add(code)
        else:
            missing.append({"code": code, "credits": it.get("credits")})

    return (len(taken), taken, missing, credited)


def eval_one_of(section: Dict[str, Any], user_codes: Set[str], user_credits: Dict[str, float]) -> Dict[str, Any]:
    """
    Evaluate a ONE_OF requirement section.
    The student must satisfy exactly one of the options (or at least one if there are multiple).

    Parameters
    ----------
    section : dict
        A ONE_OF requirement block, expected keys:
        - "options": list of options
          Each option can be:
            {"type": "COURSE", "code": "COMP SCI 400", "credits": 3}
            {"type": "ALL_OF", "items": [...]}
          where "ALL_OF" means all listed courses in that option must be taken.

    user_codes : set[str]
        All normalized course codes the student has.

    user_credits : dict
        Map of course code → credits earned/planned.

    Returns
    -------
    dict
        Requirement evaluation result with:
        - status ("complete", "in_progress", or "missing")
        - taken/missing courses
        - credited_codes
        - credits_earned
        - selected_option (which path satisfied or was closest)
    """
    # Keep track of the best partial match for guidance
    best = {
        "match": -1,      # how many courses matched
        "taken": [],
        "missing": [],
        "credited": set(),
        "complete": False,
        "selected_option": None,
    }

    # Loop over each option
    for opt in section.get("options", []):
        # Option type 1: single course
        if opt["type"] == "COURSE":
            code = normalize_code(opt["code"])
            if code in user_codes:
                # Single course satisfied → requirement complete
                return {
                    "status": "complete",
                    "taken": [{"code": code, "credits": opt.get("credits")}],
                    "missing": [],
                    "credited_codes": [code],
                    "credits_earned": user_credits.get(code, opt.get("credits", 0) or 0),
                    "selected_option": {"type": "COURSE", "code": code},
                }
            else:
                # This course not taken — record as a candidate with 0 matches if best not set yet
                if best["match"] < 0:
                    best = {
                        "match": 0,
                        "taken": [],
                        "missing": [{"code": code, "credits": opt.get("credits")}],
                        "credited": set(),
                        "complete": False,
                        "selected_option": {"type": "COURSE", "code": code},
                    }

        # Option type 2: ALL_OF sub-block
        elif opt["type"] == "ALL_OF":
            match_count, taken, missing, credited = _score_all_of(opt.get("items", []), user_codes)
            if not missing:
                # Initialize total credits earned to 0
                credits_earned = 0
                # Looping through each course in the 'taken' list
                for t in taken:
                    course_code = t["code"]  # e.g., "COMP SCI 300"
                    # We first try to get the student's actual credits from user_credits dict
                    # If not found then fallback to the credits value stored in this course dict
                    # If that is also None, fallback to 0
                    course_credits = user_credits.get(course_code, t.get("credits", 0) or 0)
                    # Add this course's credits to the running total
                    credits_earned += course_credits
                return {
                    "status": "complete",
                    "taken": taken,
                    "missing": [],
                    "credited_codes": list(credited),
                    "credits_earned": credits_earned,
                    "selected_option": {"type": "ALL_OF", "items": [x["code"] for x in taken]},
                }
            # If not complete, keep track of the option with the highest matches so far
            if match_count > best["match"]:
                best = {
                    "match": match_count,
                    "taken": taken,
                    "missing": missing,
                    "credited": credited,
                    "complete": False,
                    "selected_option": {"type": "ALL_OF"},
                }
    # If the user matched zero courses in this best option → they're "missing" it entirely.
    if best["match"] == 0:
        status = "missing"
    # If the user matched *more than zero* courses, but the option is not fully satisfied → "in_progress".
    elif best["match"] > 0:
        status = "in_progress"
    # If somehow best["match"] is still -1 (meaning no options processed properly), mark as "missing".
    else:
        status = "missing"
    # Calculate credits_earned
    credits_earned = 0.0

    for t in best["taken"]:
        course_code = t["code"]

        # Get the user's actual credits for this course from user_credits (dict: code -> credits).
        # If not found in user_credits, fall back to the credits value inside `t`.
        # If that's missing too, default to 0.
        course_credits = user_credits.get(course_code, t.get("credits", 0) or 0)

        credits_earned += course_credits

    return {
        "status": status,
        "taken": best["taken"],
        "missing": best["missing"],
        "credited_codes": list(best["credited"]),
        "credits_earned": credits_earned,
        "selected_option": best["selected_option"],
    }


def eval_n_of(section: Dict[str, Any], user_codes: Set[str], user_credits: Dict[str, float]) -> Dict[str, Any]:
    """
    Evaluate an N_OF requirement section.
    The student must take AT LEAST `n` courses from the list.

    Parameters
    ----------
    section : dict
        Requirement block with:
        - "n": number of courses required
        - "items": list of {"code": str, "credits": int}

    user_codes : set[str]
        Courses user has.

    user_credits : dict
        Course code → credits earned/planned.

    Returns
    -------
    dict
        Status, taken courses, missing courses (up to remaining needed),
        credited codes, credits earned, and counts completed/required.
    """
    n = int(section.get("n", 0))  # Number of required courses
    present = []  # Courses the user has from the list
    absent = []   # Courses the user doesn't have

    for it in section.get("items", []):
        code = normalize_code(it["code"])
        if code in user_codes:
            present.append({"code": code, "credits": it.get("credits")})
        else:
            absent.append({"code": code, "credits": it.get("credits")})

    # Only credit up to n matched courses to avoid over-crediting
    credited_slice = present[:n]
    credited_codes = {x["code"] for x in credited_slice}
    # Initialize total credits earned for this requirement section
    credits_earned = 0
    # Go through each course in 'credited_slice'
    # (which is the first N courses from 'present' that we want to count toward N_OF)
    for t in credited_slice:
        course_code = t["code"]  # e.g., "COMP SCI 400"
        # Try to get the number of credits from the student's actual planned courses
        # If not found, fall back to the credits value in the requirement definition
        # If that is also None, use 0
        course_credits = user_credits.get(course_code, t.get("credits", 0) or 0)
        # Add this course's credits to the running total
        credits_earned += course_credits


    # Figure out how many are still needed
    remaining_needed = max(n - len(present), 0)
    missing = absent[:remaining_needed] if remaining_needed > 0 else []

    # Determine status
    status = "complete" if remaining_needed == 0 else ("in_progress" if present else "missing")

    return {
        "status": status,
        "taken": present,
        "missing": missing,
        "credited_codes": list(credited_codes),
        "credits_earned": credits_earned,
        "n_required": n,
        "n_completed": min(len(present), n),
    }


# ---------- Orchestrator ----------

def evaluate_major(major_key: str, planned_courses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evaluate a user's progress for a single major .

    - Loads the major definition (its sections and rules) using `major_key`.
    - Builds fast-lookup structures from the user's planned courses:
        user_codes (set of normalized course codes)
        user_credits (dict: code -> credits)
    - For each section in the major:
        Runs the correct evaluator (ALL_OF, ONE_OF, or N_OF).
        Collects section status, taken/missing lists, etc.
        Adds the section's credits to the major total, but without doublecounting the same course across multiple sections.
    - Returns a JSON-like dict

    Parameters
    major_key : str
        Key into MAJOR_REQUIREMENTS (e.g., "CS_LS").

    planned_courses : list[dict]
        The user's courses (each must have at least "code" and "credits").

    Returns
    dict
        {
          "id": <human-readable major name>,
          "major_key": <the key we evaluated>,
          "sections": [ ... per-section results ... ],
          "major_credits_earned": <float>,
          "major_credits_target": <int>,
          "remaining_credits": <float>,
          "college_key": <the college this major belongs to, e.g., "L&S_BS">
        }
    """
    # Get this major's rule definition
    major = MAJOR_REQUIREMENTS[major_key]
    sections = major["sections"]

    #  Build user lookup structures
    user_codes, user_credits = build_user_catalog(planned_courses)

    #  Prepare results and accounting
    section_results = []  # what we'll return per section: List[Dict[str, Any]]
    used_codes = set()      # tracks which course codes already counted for credits.  Set[str]
    major_credits_earned = 0.0      # running total for the whole major

    #  Evaluate each section independently
    for sec in sections:
        # Pick the correct evaluator based on section type
        if sec["type"] == "ALL_OF":
            res = eval_all_of(sec, user_codes, user_credits)
        elif sec["type"] == "ONE_OF":
            res = eval_one_of(sec, user_codes, user_credits)
        elif sec["type"] == "N_OF":
            res = eval_n_of(sec, user_codes, user_credits)
        else:
            # Unknown section type (shouldn't happen in our data)
            res = {
                "status": "unknown",
                "taken": [],
                "missing": [],
                "credited_codes": [],
                "credits_earned": 0.0
            }

        # De duplicate credits across sections:
        #   only adding credits for course codes we haven't already counted.
        dedup_credits = 0.0
        for code in res.get("credited_codes", []):
            if code not in used_codes:
                # Adding the user's actual credits for this course 
                course_credits = user_credits.get(code, 0.0)
                dedup_credits += course_credits
                used_codes.add(code)  # mark as counted

        # Add a cleaned section result (with deduped credits)
        section_results.append({
            "id": sec["id"],
            "title": sec.get("title"),
            "type": sec["type"],
            "status": res["status"],
            "taken": res["taken"],
            "missing": res["missing"],
            "credits_earned": dedup_credits,   # already de-duplicated for this section
        })

        # Increase major total
        major_credits_earned += dedup_credits

    # 6) Compute summary numbers for the major
    target = major.get("total_major_credits", 0)
    remaining = target - major_credits_earned
    if remaining < 0:
        remaining = 0.0

    # 7) Return the full major progress payload
    return {
        "id": major["id"],
        "major_key": major_key,
        "sections": section_results,
        "major_credits_earned": major_credits_earned,
        "major_credits_target": target,
        "remaining_credits": remaining,
        "college_key": major.get("college"),
    }


def evaluate_degree(college_key: str, planned_courses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evaluate degree-level progress 

    Sums all of the user's planned/earned credits (major + GenEd + anything).
    Compares to the college's total degree credit requirement (e.g., 120 for L&S BS).
    Returns labels for Gen Ed and L&S-specific requirements (informational only for now).

    Parameters
    college_key : str
        Key into DEGREE_REQUIREMENTS (e.g., "L&S_BS").

    planned_courses : list[dict]
        The user's courses with "code" and "credits".

    Returns

    dict
        {
          "id": <college id>,
          "total_degree_credits": <target, e.g., 120>,
          "credits_completed": <sum of user's credits>,
          "credits_remaining": <target - completed>,
          "gen_ed": {...labels only for MVP...},
          "ls_specific": {...labels only for MVP...}
        }
    """
    college = DEGREE_REQUIREMENTS[college_key]

    # Sum all user credits safely
    total_user_credits = 0.0
    for c in planned_courses:
        raw = c.get("credits", 0)
        try:
            if raw is None:
                total_user_credits += 0.0
            else:
                total_user_credits += float(raw)
        except (ValueError, TypeError):
            # Bad data → treat as 0 credits
            total_user_credits += 0.0

    # Target degree credits (e.g., 120)
    target = float(college.get("total_degree_credits", 120))

    # Remaining (never below zero)
    remaining = target - total_user_credits
    if remaining < 0:
        remaining = 0.0

    # Return degree-level progress (GenEd/L&S are info-only for now)
    return {
        "id": college["id"],
        "total_degree_credits": target,
        "credits_completed": total_user_credits,
        "credits_remaining": remaining,
        "gen_ed": college.get("gen_ed", {}),
        "ls_specific": college.get("ls_specific", {}),
    }

def evaluate(college_key: str, major_key: str, planned_courses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Full evaluation used by the /progress endpoint.

 
    - Runs the major evaluation (sections with statuses, taken/missing, major credits).
    - Determines which college to use (either the one passed in, or the college tied to the major).
    - Runs the degree evaluation (sum of all credits vs target).
    - Returns BOTH results in a single JSON payload so the frontend only needs one request.

    Parameters

    college_key : str
        Optional; if None/empty, we'll infer from the major's "college" field.

    major_key : str
        Required; key for the major to evaluate (e.g., "CS_LS").

    planned_courses : list[dict]
        The user's courses with "code" and "credits".

    Returns
    dict
        {
          "college_progress": {...},
          "major_progress": {...}
        }
    """
    #  Major progress (always needs to run)
    major_progress = evaluate_major(major_key, planned_courses)

    #  Figure out which college to use:
    #     If the caller provides a college_key we use it
    #     else use the major's college (from rules data)
    if college_key:
        college_to_use = college_key
    else:
        college_to_use = major_progress.get("college_key")

    #  Degree progress
    college_progress = evaluate_degree(college_to_use, planned_courses)

    #  Combined payload for the frontend
    return {
        "college_progress": college_progress,
        "major_progress": major_progress,
    }
