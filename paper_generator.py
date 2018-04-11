import os
from fpdf import FPDF
import constants
import json
import sys


VERSION = '1.2'


class PickListPDF(FPDF):
    def __init__(self, study_method, task_order_number, is_training_task, task_id, *args, **kwargs):
        super(PickListPDF, self).__init__(*args, **kwargs)
        self.study_method = study_method
        self.task_order_number = task_order_number
        self.is_training_task = is_training_task
        self.task_id = task_id

    def header(self):
        self.set_font('Times', 'B', 15)  # Times New Roman, Bold, 15

        # Move to the right, and print title
        self.cell(w=70)
        title = study_method.replace('-', ' ').replace('_', ' - ').title()
        self.cell(w=60, h=10, txt=title, align='C', border=1, ln=0, link='C')

        # Move down, to the right, and print version number
        self.set_font('Times', 'B', 12)  # Times New Roman, Bold, 12
        self.set_y(20)
        self.cell(w=75)
        self.cell(w=50, h=10, txt='Version %s' % VERSION, align='C')

        # Line break
        self.ln(5)

    # Page footer
    def footer(self):
        self.set_font('Times', '', 10)

        self.set_xy(-60, -20)
        self.cell(w=50, h=10, txt='Task #%d' % self.task_order_number)
        self.set_xy(-60, -15)
        self.cell(w=50, h=10, txt='Task ID %d - %s' % (self.task_id, 'Training' if self.is_training_task else 'Testing'))


if __name__ == '__main__':

    # Read command line arguments
    study_method = sys.argv[1]
    task_type = sys.argv[2]

    # Create path where this JSON file exists and read the file
    path = os.path.join('.', 'RFID-Study-Task-Generation', 'output', study_method, 'tasks-%s-%s.json' % (study_method, task_type))
    with open(path, mode='r') as f:
        data = json.load(f)

    assert data['version'] == VERSION, "Version must match!"

    for i, task in enumerate(data['tasks']):

        # Setup PDF
        pdf = PickListPDF(
            study_method=study_method,
            task_order_number=i + 1,
            is_training_task='training' in path,
            task_id=task['taskId'],
        )
        pdf.alias_nb_pages()
        pdf.add_page()
        pdf.set_font('Times', '', 11)

        # Write information to PDF
        for rack in constants.RACKS:
            txt = rack
            print(txt)

            pdf.cell(w=0, h=10, txt=txt, border=0, ln=0)
            pdf.ln(h=5)

            for order in task['orders']:
                orderId = order['orderId']

                txt = ' ' * 20 + '-' * 25
                print(txt)

                pdf.cell(w=0, h=10, txt=txt, border=0, ln=0)
                pdf.ln(h=5)

                txt = ' ' * 20 + str(orderId)
                print(txt)

                pdf.cell(w=0, h=10, txt=txt, border=0, ln=0)
                pdf.ln(h=5)

                for source_bin in order['sourceBins']:
                    if source_bin['binTag'][0] != rack:
                        continue

                    txt = ' ' * 30 \
                        + "%s x %d" % (source_bin['binTag'][1:], source_bin['numItems'])

                    print(txt)

                    pdf.cell(w=0, h=10, txt=txt, border=0, ln=0)
                    pdf.ln(h=5)

                pdf.ln(h=5)

        # Create output directories if needed
        pdfs_dir = 'pdfs'
        if not os.path.isdir(pdfs_dir):
            os.mkdir(pdfs_dir)

        output_dir = os.path.join(pdfs_dir, study_method)
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)

        # Write to output file
        output_filename = os.path.join(output_dir, '%s-%s-Task-Order-Number-%d.pdf' % (study_method, task_type, i + 1))
        pdf.output(output_filename, dest='F')

        # Uncomment below to open the file (only works on macOS)
        # os.system('open %s' % output_filename)
