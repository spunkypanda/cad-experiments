"""Entry point"""

from dxf_parser import DxfParser

if __name__ == '__main__':
    parser = DxfParser('files/first.dxf')
    parser.parse()
    print(f"Seat count: {parser.get_seat_count()}")
    seats = parser.get_coords()

    seat_num = 12

    seat_12 = seats[seat_num-1]
    print(f"Seat 12: {seat_12}")

    # parser.get_exported_image("output.svg")
    # parser.export_pdf("output.pdf")
