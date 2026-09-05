"""
KoS Script Generator for KSP Flight Planner

This module generates Kerbal Operating System (KoS) scripts based on flight plans
created by the KSP Flight Planner. The generated scripts include launch sequences
with a linear ascent profile and execution of planned maneuvers.
"""

import os
import math
from datetime import datetime

def generate_kos_script(mission, spacecraft_mass=1.0, isp=300):
    """
    Generate a KoS script for the given mission.

    Args:
        mission: Mission object containing maneuvers and orbits
        spacecraft_mass: Mass of the spacecraft in tons (default 1.0)
        isp: Specific impulse of the engine in seconds (default 300)

    Returns:
        str: Complete KoS script as a string
    """

    script_lines = []

    # Header
    script_lines.append("// Generated KoS Script for Mission: " + mission.name)
    script_lines.append("// Generated on: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    script_lines.append("//")
    script_lines.append("")
    script_lines.append("// Mission parameters")
    script_lines.append("SET mission_name TO \"" + mission.name + "\".")
    script_lines.append("SET spacecraft_mass TO " + str(spacecraft_mass) + ".")
    script_lines.append("SET engine_isp TO " + str(isp) + ".")
    script_lines.append("")

    # Launch sequence if mission starts with launch
    if mission.maneuvers and mission.maneuvers[0].type == "Launch":
        script_lines.extend(_generate_launch_sequence(mission.origin(), mission.orbits[1] if len(mission.orbits) > 1 else None))

    # Execute maneuvers
    for i, maneuver in enumerate(mission.maneuvers):
        if maneuver.type == "Launch":
            continue  # Already handled above
        script_lines.extend(_generate_maneuver_code(maneuver, mission.orbits[i+1] if i+1 < len(mission.orbits) else None, spacecraft_mass, isp))

    # Footer
    script_lines.append("")
    script_lines.append("// Mission complete")
    script_lines.append("PRINT \"Mission " + mission.name + " completed successfully\".")

    return "\n".join(script_lines)


def save_kos_script(script, filename, folder="scripts"):
    """Save the generated KoS script to a file in the specified scripts folder."""
    os.makedirs(folder, exist_ok=True)
    if not filename.lower().endswith(".kos"):
        filename += ".kos"
    path = os.path.join(folder, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(script)
    return path


def _generate_launch_sequence(origin_body, target_orbit):
    """Generate the launch sequence with linear ascent profile."""
    lines = []

    lines.append("// Launch sequence")
    lines.append("PRINT \"Starting launch sequence from " + origin_body.name + "\".")
    lines.append("")

    # Pre-launch setup
    lines.append("// Pre-launch checks")
    lines.append("LOCK THROTTLE TO 0.")
    lines.append("LOCK STEERING TO UP.")
    lines.append("WAIT 1.")
    lines.append("STAGE.")
    lines.append("WAIT 1.")
    lines.append("")

    # Ascent profile
    lines.append("// Ascent profile: Linear pitch to 50° at 10km, then maintain 50°")
    lines.append("SET target_altitude TO " + str(target_orbit.a_alt if target_orbit else origin_body.standard_launch_height) + ".")
    lines.append("SET ascent_complete TO FALSE.")
    lines.append("")
    lines.append("UNTIL ascent_complete {")
    lines.append("    SET current_alt TO ALTITUDE.")
    lines.append("    ")
    lines.append("    // Calculate pitch based on altitude")
    lines.append("    IF current_alt < 10000 {")
    lines.append("        SET pitch TO 90 - (current_alt / 10000) * 40.")  # Linear from 90° to 50°
    lines.append("    } ELSE {")
    lines.append("        SET pitch TO 50.")  # Maintain 50° after 10km
    lines.append("    }")
    lines.append("    ")
    lines.append("    LOCK STEERING TO HEADING(90, pitch).")  # 90° heading (east), variable pitch
    lines.append("    ")
    lines.append("    // Throttle control")
    lines.append("    IF current_alt < target_altitude - 1000 {")
    lines.append("        LOCK THROTTLE TO 1.")
    lines.append("    } ELSE {")
    lines.append("        LOCK THROTTLE TO 0.1.")  # Gentle throttle near target
    lines.append("    }")
    lines.append("    ")
    lines.append("    // Check for apoapsis near target")
    lines.append("    IF APOAPSIS > target_altitude - 500 AND APOAPSIS < target_altitude + 500 {")
    lines.append("        LOCK THROTTLE TO 0.")
    lines.append("        SET ascent_complete TO TRUE.")
    lines.append("    }")
    lines.append("    ")
    lines.append("    WAIT 0.1.")
    lines.append("}")
    lines.append("")
    lines.append("PRINT \"Ascent complete. Apoapsis: \" + ROUND(APOAPSIS) + \"m\".")
    lines.append("")

    # Coast to apoapsis and circularize
    lines.append("// Coast to apoapsis and circularize")
    lines.append("WAIT UNTIL ETA:APOAPSIS < 30.")
    lines.append("LOCK STEERING TO PROGRADE.")
    lines.append("WAIT UNTIL ETA:APOAPSIS < 5.")
    lines.append("LOCK THROTTLE TO 1.")
    lines.append("WAIT UNTIL PERIAPSIS > target_altitude - 1000.")
    lines.append("LOCK THROTTLE TO 0.")
    lines.append("PRINT \"Orbit achieved. Periapsis: \" + ROUND(PERIAPSIS) + \"m, Apoapsis: \" + ROUND(APOAPSIS) + \"m\".")
    lines.append("")

    return lines

def _generate_maneuver_code(maneuver, target_orbit, spacecraft_mass, isp):
    """Generate simple code for a specific maneuver that works with most rockets."""
    lines = []
    maneuver_text = getattr(maneuver, 'description', None) or getattr(maneuver, 'name', str(maneuver.type))

    lines.append("// " + maneuver_text)
    lines.append("PRINT \"" + maneuver_text + "\".")
    lines.append("")

    # Simple burn execution - no complex calculations
    lines.append("// Execute burn - works for most rockets")
    lines.append("WAIT UNTIL NEXTNODE:ETA < 60.")  # Start preparing 60s before
    lines.append("LOCK STEERING TO NEXTNODE:DELTAV:DIRECTION.")
    lines.append("WAIT UNTIL NEXTNODE:ETA < 10.")  # Start burn 10s before
    lines.append("")
    lines.append("// Burn until delta-v is small")
    lines.append("LOCK THROTTLE TO 1.")
    lines.append("UNTIL NEXTNODE:DELTAV:MAG < 1 {")
    lines.append("    // Reduce throttle near end for precision")
    lines.append("    IF NEXTNODE:ETA < 1 AND NEXTNODE:DELTAV:MAG > 5 {")
    lines.append("        LOCK THROTTLE TO 0.1.")
    lines.append("    }")
    lines.append("    WAIT 0.1.")
    lines.append("}")
    lines.append("")
    lines.append("LOCK THROTTLE TO 0.")
    lines.append("UNLOCK STEERING.")
    lines.append("REMOVE NEXTNODE.")
    lines.append("PRINT \"" + maneuver_text + " completed\".")
    lines.append("")

    return lines

def _calculate_burn_time(delta_v, mass, isp):
    """
    Simple burn time estimation for KoS script.
    For generic rockets, we'll use a basic approximation.
    """
    if delta_v <= 0:
        return 1  # Minimum burn time
    
    # Rough estimate: assume 1 ton ship with 300s Isp can do ~1000 m/s delta-v in ~10s
    # Scale roughly by mass and Isp
    base_time = 10 * (delta_v / 1000) * (mass / 1.0) * (300 / isp)
    return max(base_time, 1)