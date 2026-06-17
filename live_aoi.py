import cv2
import os
from ultralytics import YOLO
from datetime import datetime
from fpdf import FPDF

# ==================================================
# CONFIGURATION
# ==================================================

MODEL_PATH = r"C:\Projects\PCB_Fault_Detection\PCB_CAM\best (2).pt"

os.makedirs("reports", exist_ok=True)
os.makedirs("snapshots", exist_ok=True)

model = YOLO(MODEL_PATH)

# ==================================================
# SCORING
# ==================================================

def calculate_score(defect_count):

    score = 100 - (defect_count * 10)

    return max(score, 0)


def get_verdict(score):

    if score >= 90:
        return "PASS"

    elif score >= 70:
        return "REVIEW"

    else:
        return "FAIL"


def get_action(verdict):

    if verdict == "PASS":
        return "Send To Production"

    elif verdict == "REVIEW":
        return "Manual Inspection Required"

    else:
        return "Reject Board"


def get_severity(defect):

    critical = [
        "missing_hole",
        "open_circuit",
        "short"
    ]

    medium = [
        "mouse_bite",
        "spur",
        "spurious_copper"
    ]

    if defect in critical:
        return "CRITICAL"

    if defect in medium:
        return "MEDIUM"

    return "LOW"

# ==================================================
# PDF REPORT
# ==================================================

def generate_pdf_report(
    result,
    pcb_id,
    operator="Rethika"):

    pdf = FPDF()

    pdf.add_page()

# ==================================
# HEADER
# ==================================

    pdf.set_font("Helvetica", "B", 18)

    pdf.cell(
    0,
    12,
    "PCB AUTOMATED INSPECTION REPORT",
    new_x="LMARGIN",
    new_y="NEXT",
    align="C"
    )

    pdf.line(10, 25, 200, 25)

    pdf.ln(5)

    # ==================================
    # BOARD INFO
    # ==================================

    pdf.set_font("Helvetica", "", 12)

    pdf.cell(
        0,
        8,
        f"PCB ID: {pcb_id}",
        new_x="LMARGIN",
        new_y="NEXT"
    )

    pdf.cell(
        0,
        8,
        f"Operator: {operator}",
        new_x="LMARGIN",
        new_y="NEXT"
    )

    pdf.cell(
        0,
        8,
        f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        new_x="LMARGIN",
        new_y="NEXT"
    )

    pdf.cell(
        0,
        8,
        "Model: YOLOv8 PCB AOI",
        new_x="LMARGIN",
        new_y="NEXT"
    )

    pdf.ln(5)

    # ==================================
    # VERDICT BOX
    # ==================================

    verdict = result["verdict"]

    if verdict == "PASS":
        pdf.set_fill_color(0, 200, 0)

    elif verdict == "REVIEW":
        pdf.set_fill_color(255, 180, 0)

    else:
        pdf.set_fill_color(220, 0, 0)

    pdf.set_font("Helvetica", "B", 14)

    pdf.cell(
        0,
        12,
        f"VERDICT : {verdict}     SCORE : {result['score']}",
        fill=True,
        align="C",
        new_x="LMARGIN",
        new_y="NEXT"
    )

    pdf.ln(5)

    # ==================================
    # IMAGE
    # ==================================

    pdf.set_font("Helvetica", "B", 13)

    pdf.cell(
        0,
        8,
        "Annotated PCB Inspection",
        new_x="LMARGIN",
        new_y="NEXT"
    )

    pdf.image(
        result["annotated_image"],
        x=15,
        w=170
    )

    pdf.ln(95)

# ==================================
# STATISTICS
# ==================================

    total_defects = sum(
        result["defects"].values()
    )

    pdf.set_font("Helvetica", "B", 13)

    pdf.cell(
        0,
        8,
        "Inspection Statistics",
        new_x="LMARGIN",
        new_y="NEXT"
    )

    pdf.set_font("Helvetica", "", 11)

    pdf.cell(
        0,
        8,
        f"Total Defects: {total_defects}",
        new_x="LMARGIN",
        new_y="NEXT"
    )

    pdf.cell(
        0,
        8,
        f"Quality Score: {result['score']}",
        new_x="LMARGIN",
        new_y="NEXT"
    )

    pdf.ln(5)

    # ==================================
    # DEFECT TABLE
    # ==================================

    pdf.set_font("Helvetica", "B", 12)

    pdf.cell(
        80,
        8,
        "Defect",
        border=1
    )

    pdf.cell(
        40,
        8,
        "Count",
        border=1
    )

    pdf.cell(
        50,
        8,
        "Severity",
        border=1
    )

    pdf.ln()

    pdf.set_font("Helvetica", "", 11)

    if len(result["defects"]) == 0:

        pdf.cell(
            170,
            8,
            "No Defects Detected",
            border=1
        )

        pdf.ln()

    else:

        for defect, count in result["defects"].items():

            pdf.cell(
                80,
                8,
                defect,
                border=1
            )

            pdf.cell(
                40,
                8,
                str(count),
                border=1
            )

            pdf.cell(
                50,
                8,
                get_severity(defect),
                border=1
            )

            pdf.ln()

    pdf.ln(5)

    # ==================================
    # EXECUTIVE SUMMARY
    # ==================================

    pdf.set_font(
        "Helvetica",
        "B",
        13
    )

    pdf.cell(
        0,
        8,
        "Executive Summary",
        new_x="LMARGIN",
        new_y="NEXT"
    )

    pdf.set_font(
        "Helvetica",
        "",
        11
    )

    summary = (
        f"{total_defects} defect(s) were detected during inspection. "
        f"The PCB achieved a quality score of {result['score']} "
        f"and received a verdict of {result['verdict']}."
    )

    pdf.multi_cell(
        0,
        7,
        summary
    )

    pdf.ln(3)

    pdf.multi_cell(
        0,
        7,
        f"Recommended Action: {get_action(result['verdict'])}"
    )

    pdf.ln(5)

    # ==================================
    # FOOTER
    # ==================================

    pdf.set_font(
        "Helvetica",
        "I",
        9
    )

    pdf.cell(
        0,
        8,
        "Automatically Generated by PCB AOI System",
        align="C"
    )

    pdf_path = f"reports/{pcb_id}.pdf"

    pdf.output(pdf_path)

    print(
        f"\nPDF Saved: {pdf_path}"
    )
# ==================================================
# WEBCAM AOI
# ==================================================

cap = cv2.VideoCapture(0)

print("\nPress S to inspect and generate report")
print("Press Q to quit\n")

while True:

    ret, frame = cap.read()

    if not ret:
        break

    results = model.predict(
        frame,
        conf=0.25,
        verbose=False
    )

    r = results[0]

    annotated = r.plot()

    defect_count = len(r.boxes)

    score = calculate_score(defect_count)

    verdict = get_verdict(score)

    cv2.putText(
        annotated,
        f"Score: {score}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.putText(
        annotated,
        f"Verdict: {verdict}",
        (20, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.imshow(
        "PCB AOI Inspection",
        annotated
    )

    key = cv2.waitKey(1) & 0xFF

    # ===================================
    # SAVE INSPECTION
    # ===================================

    if key == ord("s"):

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        pcb_id = f"PCB_{timestamp}"

        raw_image = (
            f"snapshots/{pcb_id}.jpg"
        )

        annotated_image = (
            f"snapshots/{pcb_id}_annotated.jpg"
        )

        cv2.imwrite(
            raw_image,
            frame
        )

        cv2.imwrite(
            annotated_image,
            annotated
        )

        defects = {}

        if len(r.boxes) > 0:

            for cls in r.boxes.cls:

                class_id = int(cls)

                class_name = model.names[class_id]

                defects[class_name] = (
                    defects.get(class_name, 0)
                    + 1
                )

        result = {

            "score": score,
            "verdict": verdict,
            "defects": defects,
            "annotated_image":
            annotated_image

        }

        generate_pdf_report(
            result,
            pcb_id=pcb_id,
            operator="Rethika"
        )

        print(
            f"Inspection completed: {pcb_id}"
        )

    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()