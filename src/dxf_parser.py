"""DXF Parser module."""

import ezdxf
from ezdxf.addons.drawing import Frontend, RenderContext, svg, layout
from ezdxf.addons.drawing import pymupdf, config


class DxfParser:
    def __init__(self, path):
        self.path = path
        self.doc = None
        self.msp = None
        self.blockrefs = None
        self.coords = []

    def parse(self):
        try:
            self.doc = ezdxf.readfile(self.path)
        except IOError:
            raise ValueError('Not a DXF file or a generic I/O error.')
        except ezdxf.DXFStructureError:
            raise ValueError('Invalid or corrupted DXF file.')

        self.msp = self.doc.modelspace()
        self.blockrefs = self.msp.query('INSERT[name=="TWOBYFOUR"]')
        # self.coords = [block.dxf.insert for block in self.blockrefs]

        self.layout = self.doc.layout()

        #self.paperspace_attribs = self.msp.entitydb.get('PAPERSPACE').attribs
        self.coords = [block.dxfattribs().get('insert') for block in self.blockrefs]

        """
        blockrefs = [block.dxfattribs() for block in self.blockrefs]
        self.coords = [blockref.get('insert') for blockref in tqdm(blockrefs)]
        """

        return self.coords

    def get_coords(self):
        return self.coords

    def get_seat_count(self) -> int:
        return len(self.coords)

    def get_exported_image(self, output_filename: str) -> None:
        export_doc = ezdxf.new()
        msp = self.doc.modelspace()
        # 1. create the render context
        context = RenderContext(self.doc)
        # 2. create the backend
        backend = svg.SVGBackend()
        # backend = dxf.DXFBackend(export_doc.modelspace())
        # 3. create the frontend
        frontend = Frontend(context, backend)
        # 4. draw the modelspace
        frontend.draw_layout(msp)
        # 5. create an A4 page layout, not required for all backends
        page = layout.Page(210, 297, layout.Units.mm, margins=layout.Margins.all(20))
        # 6. get the SVG rendering as string - this step is backend dependent
        svg_string = backend.get_string(page)
        with open(output_filename, "wt", encoding="utf8") as fp:
            fp.write(svg_string)

        # # 5. save or return DXF document
        # export_doc.saveas("output_01.dxf")


        return None

    def export_pdf(self, output_filename: str) -> None:
        msp = self.doc.modelspace()
        # 1. create the render context
        context = RenderContext(self.doc)
        # 2. create the backend
        backend = pymupdf.PyMuPdfBackend()
        # 3. create the frontend
        frontend = Frontend(context, backend)
        # 4. draw the modelspace
        frontend.draw_layout(msp)
        # 5. create an A0 page layout
        pg_size = layout.PAGE_SIZES.get("ISO A0")
        page = layout.Page(*pg_size, margins=layout.Margins.all(20))
        # 6. get the PDF rendering as bytes
        pdf_bytes = backend.get_pdf_bytes(page)
        with open(output_filename, "wb") as fp:
            fp.write(pdf_bytes)

    def get_blockrefs(self):
        return self.blockrefs

    def get_msp(self):
        return self.msp

    def get_doc(self):
        return self.doc

    def get_path(self):
        return self.path

    def __str__(self):
        return f"Path: {self.path}"
