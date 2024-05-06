"""DXF Parser module."""

import ezdxf
from ezdxf.addons.drawing import Frontend, RenderContext, svg, layout
from ezdxf.addons.drawing import pymupdf, config
from ezdxf.math import Vec3
from ezdxf import bbox

def get_arbitrary_orthogonal_vectors(entity):
    Az = Vec3(entity.dxf.extrusion).normalize()  # normal (extrusion) vector
    if (abs(Az.x) < 1/64.) and (abs(Az.y) < 1/64.):
        Ax = Vec3(0, 1, 0).cross(Az).normalize()  # the cross-product operator
    else:
        Ax = Vec3(0, 0, 1).cross(Az).normalize()  # the cross-product operator
    Ay = Az.cross(Ax).normalize()
    return (Ax, Ay, Az)


def wcs_to_ocs(axes, point):
    Ax, Ay, Az = axes
    px, py, pz = Vec3(point)  # point in WCS
    x = px * Ax.x + py * Ax.y + pz * Ax.z
    y = px * Ay.x + py * Ay.y + pz * Ay.z
    z = px * Az.x + py * Az.y + pz * Az.z
    return Vec3(x, y, z)


# Wx = wcs_to_ocs((1, 0, 0))
# Wy = wcs_to_ocs((0, 1, 0))
# Wz = wcs_to_ocs((0, 0, 1))


def ocs_to_wcs(axes, point):
    (Wx, Wy, Wz) = axes
    px, py, pz = Vec3(point)  # point in OCS
    x = px * Wx.x + py * Wx.y + pz * Wx.z
    y = px * Wy.x + py * Wy.y + pz * Wy.z
    z = px * Wz.x + py * Wz.y + pz * Wz.z
    return Vec3(x, y, z)


def convert_to_wcs(entity):
    # if entity.dxf.hasattr('extrusion'):
    #     return wcs_to_ocs(entity.dxf.insert)
    # else:
    #     return entity.dxf.insert

    Ax, Ay, Az = get_arbitrary_orthogonal_vectors(entity)
    axes = Ax, Ay, Az

    Wx = wcs_to_ocs(axes, (1, 0, 0))
    Wy = wcs_to_ocs(axes, (0, 1, 0))
    Wz = wcs_to_ocs(axes, (0, 0, 1))

    return ocs_to_wcs((Wx, Wy, Wz), entity.dxf.insert)


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
        self.blockrefsattribs = [block.dxfattribs() for block in self.blockrefs]

        boxed = bbox.extents(self.blockrefs)

        self.bbb = [convert_to_wcs(block) for block in self.msp.query('INSERT[name=="TWOBYFOUR"]')]

        """
        self.coords = [blockref.get('insert') for blockref in tqdm(blockrefs)]
        """

        self.ccc = [b for b in self.bbb]

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
