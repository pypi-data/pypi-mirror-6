import glob
import json
import os
from unittest import TestCase
import unittest
from pymatgen import Molecule
from pymatgen.io.qchemio import QcInput, QcBatchInput, QcOutput

__author__ = 'xiaohuiqu'


test_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..",
                        'test_files', "molecules")


coords = [[0.000000, 0.000000, 0.000000],
          [0.000000, 0.000000, 1.089000],
          [1.026719, 0.000000, -0.363000],
          [-0.513360, -0.889165, -0.363000],
          [-0.513360, 0.889165, -0.363000]]
mol = Molecule(["C", "H", "H", "H", "Cl"], coords)

coords2 = [[0.0, 0.0, -2.4],
          [0.0, 0.0, 0.0],
          [0.0, 0.0, 2.4]]
heavy_mol = Molecule(["Br", "Cd", "Br"], coords2)


class TestQcInput(TestCase):

    def elementary_io_verify(self, text, qcinp):
        self.to_and_from_dict_verify(qcinp)
        self.from_string_verify(contents=text, ref_dict=qcinp.to_dict)

    def to_and_from_dict_verify(self, qcinp):
        """
        Helper function. This function should be called in each specific test.
        """
        d1 = qcinp.to_dict
        qc2 = QcInput.from_dict(d1)
        d2 = qc2.to_dict
        self.assertEqual(d1, d2)

    def from_string_verify(self, contents, ref_dict):
        qcinp = QcInput.from_string(contents)
        d2 = qcinp.to_dict
        self.assertEqual(ref_dict, d2)

    def test_read_zmatrix(self):
        contents = '''$moLEcule

 1 2

 S
 C  1 1.726563
 H  2 1.085845 1 119.580615
 C  2 1.423404 1 114.230851 3 -180.000000 0
 H  4 1.084884 2 122.286346 1 -180.000000 0
 C  4 1.381259 2 112.717365 1 0.000000 0
 H  6 1.084731 4 127.143779 2 -180.000000 0
 C  6 1.415867 4 110.076147 2 0.000000 0
 F  8 1.292591 6 124.884374 4 -180.000000 0
$end

$reM
   BASIS  =  6-31+G*
   EXCHANGE  =  B3LYP
   jobtype  =  freq
$end

'''
        qcinp = QcInput.from_string(contents)
        ans = '''$molecule
 1  2
 S           0.00000000        0.00000000        0.00000000
 C           0.00000000        0.00000000        1.72656300
 H          -0.94431813        0.00000000        2.26258784
 C           1.29800105       -0.00000002        2.31074808
 H           1.45002821       -0.00000002        3.38492732
 C           2.30733813       -0.00000003        1.36781908
 H           3.37622632       -0.00000005        1.55253338
 C           1.75466906       -0.00000003        0.06427152
 F           2.44231414       -0.00000004       -1.03023099
$end


$rem
   jobtype = freq
  exchange = b3lyp
     basis = 6-31+g*
$end

'''
        ans_tokens = ans.split('\n')
        ans_text_part = ans_tokens[:2] + ans_tokens[11:]
        ans_coords_part = ans_tokens[2:11]
        converted_tokens = str(qcinp).split('\n')
        converted_text_part = converted_tokens[:2] + converted_tokens[11:]
        converted_coords_part = converted_tokens[2:11]
        self.assertEqual(ans_text_part, converted_text_part)
        for ans_coords, converted_coords in zip(ans_coords_part,
                                                converted_coords_part):
            ans_coords_tokens = ans_coords.split()
            converted_coords_tokens = converted_coords.split()
            self.assertEqual(ans_coords_tokens[0], converted_coords_tokens[0])
            xyz1 = ans_coords_tokens[1:]
            xyz2 = converted_coords_tokens[1:]
            for t1, t2 in zip(xyz1, xyz2):
                self.assertTrue(abs(float(t1)-float(t2)) < 0.0001)

    def test_no_mol(self):
        ans = '''$comments
 Test Methane
$end


$molecule
 -1  2
 read
$end


$rem
   jobtype = sp
  exchange = b3lyp
     basis = 6-31+g*
$end

'''
        qcinp = QcInput(molecule="READ", title="Test Methane",
                        exchange="B3LYP", jobtype="SP", charge=-1,
                        spin_multiplicity=2,
                        basis_set="6-31+G*")
        self.assertEqual(str(qcinp), ans)
        self.elementary_io_verify(ans, qcinp)

    def test_simple_basis_str(self):
        ans = '''$comments
 Test Methane
$end


$molecule
 0  1
 C           0.00000000        0.00000000        0.00000000
 H           0.00000000        0.00000000        1.08900000
 H           1.02671900        0.00000000       -0.36300000
 H          -0.51336000       -0.88916500       -0.36300000
 Cl         -0.51336000        0.88916500       -0.36300000
$end


$rem
   jobtype = sp
  exchange = b3lyp
     basis = 6-31+g*
$end

'''
        qcinp = QcInput(mol, title="Test Methane", exchange="B3LYP",
                        jobtype="SP",
                        basis_set="6-31+G*")
        self.assertEqual(str(qcinp), ans)
        self.elementary_io_verify(ans, qcinp)

    def test_aux_basis_str(self):
        ans = '''$comments
 Test Methane
$end


$molecule
 0  1
 C           0.00000000        0.00000000        0.00000000
 H           0.00000000        0.00000000        1.08900000
 H           1.02671900        0.00000000       -0.36300000
 H          -0.51336000       -0.88916500       -0.36300000
 Cl         -0.51336000        0.88916500       -0.36300000
$end


$rem
    jobtype = freq
   exchange = xygjos
      basis = gen
  aux_basis = gen
$end


$aux_basis
 C
 rimp2-cc-pvdz
 ****
 Cl
 rimp2-aug-cc-pvdz
 ****
 H
 rimp2-cc-pvdz
 ****
$end


$basis
 C
 6-31g*
 ****
 Cl
 6-31+g*
 ****
 H
 6-31g*
 ****
$end

'''
        qcinp = QcInput(mol, title="Test Methane", exchange="xygjos",
                        jobtype="Freq",
                        basis_set={"C": "6-31G*", "h": "6-31g*",
                                   "CL": "6-31+g*"},
                        aux_basis_set={"c": "rimp2-cc-pvdz",
                                       "H": "rimp2-cc-pvdz",
                                       "Cl": "rimp2-aug-cc-pvdz"})
        self.assertEqual(str(qcinp), ans)
        self.elementary_io_verify(ans, qcinp)

    def test_ecp_str(self):
        ans = '''$comments
 Test ECP
$end


$molecule
 0  1
 Br          0.00000000        0.00000000       -2.40000000
 Cd          0.00000000        0.00000000        0.00000000
 Br          0.00000000        0.00000000        2.40000000
$end


$rem
   jobtype = opt
  exchange = b3lyp
     basis = gen
       ecp = gen
$end


$basis
 Br
 srlc
 ****
 Cd
 srsc
 ****
$end


$ecp
 Br
 srlc
 ****
 Cd
 srsc
 ****
$end

'''
        qcinp = QcInput(heavy_mol, title="Test ECP", exchange="B3LYP",
                        jobtype="Opt",
                        basis_set={"Br": "srlc", "Cd": "srsc"},
                        ecp={"Br": "SrlC", "Cd": "srsc"})
        self.assertEqual(str(qcinp), ans)
        self.elementary_io_verify(ans, qcinp)

    def test_set_memory(self):
        ans = '''$comments
 Test Methane
$end


$molecule
 0  1
 C           0.00000000        0.00000000        0.00000000
 H           0.00000000        0.00000000        1.08900000
 H           1.02671900        0.00000000       -0.36300000
 H          -0.51336000       -0.88916500       -0.36300000
 Cl         -0.51336000        0.88916500       -0.36300000
$end


$rem
     jobtype = sp
    exchange = b3lyp
       basis = 6-31+g*
  mem_static = 500
   mem_total = 18000
$end

'''
        qcinp = QcInput(mol, title="Test Methane", exchange="B3LYP",
                        jobtype="SP",
                        basis_set="6-31+G*")
        qcinp.set_memory(total=18000, static=500)
        self.assertEqual(str(qcinp), ans)
        self.elementary_io_verify(ans, qcinp)

    def test_set_max_num_of_scratch_files(self):
        ans = '''$comments
 Test Methane
$end


$molecule
 0  1
 C           0.00000000        0.00000000        0.00000000
 H           0.00000000        0.00000000        1.08900000
 H           1.02671900        0.00000000       -0.36300000
 H          -0.51336000       -0.88916500       -0.36300000
 Cl         -0.51336000        0.88916500       -0.36300000
$end


$rem
           jobtype = sp
          exchange = b3lyp
             basis = 6-31+g*
  max_sub_file_num = 500
$end

'''
        qcinp = QcInput(mol, title="Test Methane", exchange="B3LYP",
                        jobtype="SP",
                        basis_set="6-31+G*")
        qcinp.set_max_num_of_scratch_files(500)
        self.assertEqual(str(qcinp), ans)
        self.elementary_io_verify(ans, qcinp)

    def test_set_max_scf_iterations(self):
        ans = '''$comments
 Test Methane
$end


$molecule
 0  1
 C           0.00000000        0.00000000        0.00000000
 H           0.00000000        0.00000000        1.08900000
 H           1.02671900        0.00000000       -0.36300000
 H          -0.51336000       -0.88916500       -0.36300000
 Cl         -0.51336000        0.88916500       -0.36300000
$end


$rem
         jobtype = sp
        exchange = b3lyp
           basis = 6-31+g*
  max_scf_cycles = 100
   scf_algorithm = diis_gdm
$end

'''
        qcinp = QcInput(mol, title="Test Methane", exchange="B3LYP",
                        jobtype="SP",
                        basis_set="6-31+G*")
        qcinp.set_scf_algorithm_and_iterations(algorithm="diis_gdm",
                                               iterations=100)
        self.assertEqual(str(qcinp), ans)
        self.elementary_io_verify(ans, qcinp)

    def test_set_scf_convergence_threshold(self):
        ans = '''$comments
 Test Methane
$end


$molecule
 0  1
 C           0.00000000        0.00000000        0.00000000
 H           0.00000000        0.00000000        1.08900000
 H           1.02671900        0.00000000       -0.36300000
 H          -0.51336000       -0.88916500       -0.36300000
 Cl         -0.51336000        0.88916500       -0.36300000
$end


$rem
          jobtype = sp
         exchange = b3lyp
            basis = 6-31+g*
  scf_convergence = 8
$end

'''
        qcinp = QcInput(mol, title="Test Methane", exchange="B3LYP",
                        jobtype="SP",
                        basis_set="6-31+G*")
        qcinp.set_scf_convergence_threshold(exponent=8)
        self.assertEqual(str(qcinp), ans)
        self.elementary_io_verify(ans, qcinp)

    def test_set_integral_threshold(self):
        ans = '''$comments
 Test Methane
$end


$molecule
 0  1
 C           0.00000000        0.00000000        0.00000000
 H           0.00000000        0.00000000        1.08900000
 H           1.02671900        0.00000000       -0.36300000
 H          -0.51336000       -0.88916500       -0.36300000
 Cl         -0.51336000        0.88916500       -0.36300000
$end


$rem
   jobtype = sp
  exchange = b3lyp
     basis = 6-31+g*
    thresh = 14
$end

'''
        qcinp = QcInput(mol, title="Test Methane", exchange="B3LYP",
                        jobtype="SP",
                        basis_set="6-31+G*")
        qcinp.set_integral_threshold(thresh=14)
        self.assertEqual(str(qcinp), ans)
        self.elementary_io_verify(ans, qcinp)

    def test_set_dft_grid(self):
        ans = '''$comments
 Test Methane
$end


$molecule
 0  1
 C           0.00000000        0.00000000        0.00000000
 H           0.00000000        0.00000000        1.08900000
 H           1.02671900        0.00000000       -0.36300000
 H          -0.51336000       -0.88916500       -0.36300000
 Cl         -0.51336000        0.88916500       -0.36300000
$end


$rem
   jobtype = sp
  exchange = b3lyp
     basis = 6-31+g*
   xc_grid = 000110000590
$end

'''
        qcinp = QcInput(mol, title="Test Methane", exchange="B3LYP",
                        jobtype="SP",
                        basis_set="6-31+G*")
        qcinp.set_dft_grid(radical_points=110, angular_points=590)
        self.assertEqual(str(qcinp), ans)
        self.elementary_io_verify(ans, qcinp)

    def test_set_scf_initial_guess(self):
        ans = '''$comments
 Test Methane
$end


$molecule
 0  1
 C           0.00000000        0.00000000        0.00000000
 H           0.00000000        0.00000000        1.08900000
 H           1.02671900        0.00000000       -0.36300000
 H          -0.51336000       -0.88916500       -0.36300000
 Cl         -0.51336000        0.88916500       -0.36300000
$end


$rem
    jobtype = sp
   exchange = b3lyp
      basis = 6-31+g*
  scf_guess = gwh
$end

'''
        qcinp = QcInput(mol, title="Test Methane", exchange="B3LYP",
                        jobtype="SP",
                        basis_set="6-31+G*")
        qcinp.set_scf_initial_guess("GWH")
        self.assertEqual(str(qcinp), ans)
        self.elementary_io_verify(ans, qcinp)

    def test_geom_opt_max_cycles(self):
        ans = '''$comments
 Test Methane
$end


$molecule
 1  2
 C           0.00000000        0.00000000        0.00000000
 H           0.00000000        0.00000000        1.08900000
 H           1.02671900        0.00000000       -0.36300000
 H          -0.51336000       -0.88916500       -0.36300000
 Cl         -0.51336000        0.88916500       -0.36300000
$end


$rem
              jobtype = sp
             exchange = b3lyp
                basis = 6-31+g*
  geom_opt_max_cycles = 100
$end

'''
        qcinp = QcInput(mol, title="Test Methane", exchange="B3LYP",
                        jobtype="SP", charge=1, spin_multiplicity=2,
                        basis_set="6-31+G*")
        qcinp.set_geom_max_iterations(100)
        self.assertEqual(str(qcinp), ans)
        self.elementary_io_verify(ans, qcinp)

    def test_set_geom_opt_coords_type(self):
        ans = '''$comments
 Test Methane
$end


$molecule
 0  1
 C           0.00000000        0.00000000        0.00000000
 H           0.00000000        0.00000000        1.08900000
 H           1.02671900        0.00000000       -0.36300000
 H          -0.51336000       -0.88916500       -0.36300000
 Cl         -0.51336000        0.88916500       -0.36300000
$end


$rem
          jobtype = sp
         exchange = b3lyp
            basis = 6-31+g*
  geom_opt_coords = 0
$end

'''
        qcinp = QcInput(mol, title="Test Methane", exchange="B3LYP",
                        jobtype="SP",
                        basis_set="6-31+G*")
        qcinp.set_geom_opt_coords_type("cartesian")
        self.assertEqual(str(qcinp), ans)
        self.elementary_io_verify(ans, qcinp)

    def test_scale_geom_opt_threshold(self):
        ans = '''$comments
 Test Methane
$end


$molecule
 0  1
 C           0.00000000        0.00000000        0.00000000
 H           0.00000000        0.00000000        1.08900000
 H           1.02671900        0.00000000       -0.36300000
 H          -0.51336000       -0.88916500       -0.36300000
 Cl         -0.51336000        0.88916500       -0.36300000
$end


$rem
                    jobtype = sp
                   exchange = b3lyp
                      basis = 6-31+g*
  geom_opt_tol_displacement = 120
        geom_opt_tol_energy = 10
      geom_opt_tol_gradient = 30
$end

'''
        qcinp = QcInput(mol, title="Test Methane", exchange="B3LYP",
                        jobtype="SP",
                        basis_set="6-31+G*")
        qcinp.scale_geom_opt_threshold(gradient=0.1, displacement=0.1,
                                       energy=0.1)
        self.assertEqual(str(qcinp), ans)
        self.elementary_io_verify(ans, qcinp)

    def test_set_geom_opt_use_gdiis(self):
        ans = '''$comments
 Test Methane
$end


$molecule
 0  1
 C           0.00000000        0.00000000        0.00000000
 H           0.00000000        0.00000000        1.08900000
 H           1.02671900        0.00000000       -0.36300000
 H          -0.51336000       -0.88916500       -0.36300000
 Cl         -0.51336000        0.88916500       -0.36300000
$end


$rem
            jobtype = sp
           exchange = b3lyp
              basis = 6-31+g*
  geom_opt_max_diis = -1
$end

'''
        qcinp = QcInput(mol, title="Test Methane", exchange="B3LYP",
                        jobtype="SP",
                        basis_set="6-31+G*")
        qcinp.set_geom_opt_use_gdiis()
        self.assertEqual(str(qcinp), ans)
        self.elementary_io_verify(ans, qcinp)

    def test_disable_symmetry(self):
        ans = '''$comments
 Test Methane
$end


$molecule
 0  1
 C           0.00000000        0.00000000        0.00000000
 H           0.00000000        0.00000000        1.08900000
 H           1.02671900        0.00000000       -0.36300000
 H          -0.51336000       -0.88916500       -0.36300000
 Cl         -0.51336000        0.88916500       -0.36300000
$end


$rem
     jobtype = sp
    exchange = b3lyp
       basis = 6-31+g*
  sym_ignore = True
    symmetry = False
$end

'''
        qcinp = QcInput(mol, title="Test Methane", exchange="B3LYP",
                        jobtype="SP",
                        basis_set="6-31+G*")
        qcinp.disable_symmetry()
        self.assertEqual(str(qcinp), ans)
        self.elementary_io_verify(ans, qcinp)

    def test_use_cosmo(self):
        ans = '''$comments
 Test Methane
$end


$molecule
 0  1
 C           0.00000000        0.00000000        0.00000000
 H           0.00000000        0.00000000        1.08900000
 H           1.02671900        0.00000000       -0.36300000
 H          -0.51336000       -0.88916500       -0.36300000
 Cl         -0.51336000        0.88916500       -0.36300000
$end


$rem
             jobtype = sp
            exchange = b3lyp
               basis = 6-31+g*
  solvent_dielectric = 35.0
      solvent_method = cosmo
$end

'''
        qcinp = QcInput(mol, title="Test Methane", exchange="B3LYP",
                        jobtype="SP",
                        basis_set="6-31+G*")
        qcinp.use_cosmo(dielectric_constant=35.0)
        self.assertEqual(str(qcinp), ans)
        self.elementary_io_verify(ans, qcinp)

    def test_use_pcm(self):
        ans = '''$comments
 Test Methane
$end


$molecule
 0  1
 C           0.00000000        0.00000000        0.00000000
 H           0.00000000        0.00000000        1.08900000
 H           1.02671900        0.00000000       -0.36300000
 H          -0.51336000       -0.88916500       -0.36300000
 Cl         -0.51336000        0.88916500       -0.36300000
$end


$rem
         jobtype = sp
        exchange = b3lyp
           basis = 6-31+g*
  solvent_method = pcm
$end


$pcm
     radii   uff
    theory   ssvpe
  vdwscale   1.1
$end


$pcm_solvent
  dielectric   78.3553
$end

'''
        qcinp = QcInput(mol, title="Test Methane", exchange="B3LYP",
                        jobtype="SP",
                        basis_set="6-31+G*")
        qcinp.use_pcm()
        self.assertEqual(str(qcinp), ans)
        self.elementary_io_verify(ans, qcinp)

        qcinp = QcInput(mol, title="Test Methane", exchange="B3LYP",
                        jobtype="SP",
                        basis_set="6-31+G*")
        qcinp.use_pcm(pcm_params={"Radii": "FF",
                                  "Theory": "CPCM",
                                  "SASrad": 1.5,
                                  "HPoints": 1202},
                      solvent_params={"Dielectric": 20.0,
                                      "Temperature": 300.75,
                                      "NSolventAtoms": 2,
                                      "SolventAtom": [[8, 1, 186, 1.30],
                                                      [1, 2, 187, 1.01]]},
                      radii_force_field="OPLSAA")
        ans = '''$comments
 Test Methane
$end


$molecule
 0  1
 C           0.00000000        0.00000000        0.00000000
 H           0.00000000        0.00000000        1.08900000
 H           1.02671900        0.00000000       -0.36300000
 H          -0.51336000       -0.88916500       -0.36300000
 Cl         -0.51336000        0.88916500       -0.36300000
$end


$rem
         jobtype = sp
        exchange = b3lyp
           basis = 6-31+g*
      force_fied = oplsaa
  solvent_method = pcm
$end


$pcm
   hpoints   1202
     radii   bondi
    sasrad   1.5
    theory   cpcm
  vdwscale   1.1
$end


$pcm_solvent
     dielectric   20.0
  nsolventatoms   2
    solventatom   8    1    186  1.30
    solventatom   1    2    187  1.01
    temperature   300.75
$end

'''
        self.assertEqual(str(qcinp), ans)
        self.elementary_io_verify(ans, qcinp)


class TestQcBatchInput(TestCase):
    def test_str_and_from_string(self):
        ans = '''$comments
 Test Methane Opt
$end


$molecule
 0  1
 C           0.00000000        0.00000000        0.00000000
 H           0.00000000        0.00000000        1.08900000
 H           1.02671900        0.00000000       -0.36300000
 H          -0.51336000       -0.88916500       -0.36300000
 Cl         -0.51336000        0.88916500       -0.36300000
$end


$rem
   jobtype = opt
  exchange = b3lyp
     basis = 6-31+g*
$end


@@@


$comments
 Test Methane Frequency
$end


$molecule
 read
$end


$rem
   jobtype = freq
  exchange = b3lyp
     basis = 6-31+g*
$end


@@@


$comments
 Test Methane Single Point Energy
$end


$molecule
 read
$end


$rem
   jobtype = sp
  exchange = b3lyp
     basis = 6-311+g(3df,2p)
$end

'''
        qcinp1 = QcInput(mol, title="Test Methane Opt", exchange="B3LYP",
                         jobtype="Opt", basis_set="6-31+G*")
        qcinp2 = QcInput(molecule="read", title="Test Methane Frequency",
                         exchange="B3LYP", jobtype="Freq", basis_set="6-31+G*")
        qcinp3 = QcInput(title="Test Methane Single Point Energy",
                         exchange="B3LYP", jobtype="SP",
                         basis_set="6-311+G(3df,2p)")
        qcbat1 = QcBatchInput(jobs=[qcinp1, qcinp2, qcinp3])
        self.assertEqual(str(qcbat1), ans)
        qcbat2 = QcBatchInput.from_string(ans)
        self.assertEqual(qcbat1.to_dict, qcbat2.to_dict)

    def test_to_and_from_dict(self):
        qcinp1 = QcInput(mol, title="Test Methane Opt", exchange="B3LYP",
                         jobtype="Opt", basis_set="6-31+G*")
        qcinp2 = QcInput(molecule="read", title="Test Methane Frequency",
                         exchange="B3LYP", jobtype="Freq",
                         basis_set="6-31+G*")
        qcinp3 = QcInput(title="Test Methane Single Point Energy",
                         exchange="B3LYP", jobtype="SP",
                         basis_set="6-311+G(3df,2p)")
        qcbat1 = QcBatchInput(jobs=[qcinp1, qcinp2, qcinp3])
        d1 = qcbat1.to_dict
        qcbat2 = QcBatchInput.from_dict(d1)
        d2 = qcbat2.to_dict
        self.assertEqual(d1, d2)


class TestQcOutput(TestCase):
    def test_energy(self):
        ref_energies_text = '''
{
    "hf-rimp2.qcout": {
        "RIMP2": -2726.6860779805256,
        "SCF": -2721.541435904716
    },
    "hf_b3lyp.qcout": {
        "SCF": -2733.1747178920828
    },
    "hf_ccsd(t).qcout": {
        "CCSD": -2726.7627121001865,
        "CCSD(T)": -2726.8283514003333,
        "MP2": -2726.685664155242,
        "SCF": -2721.5414360843106
    },
    "hf_cosmo.qcout": {
        "SCF": -2721.1752937496067
    },
    "hf_hf.qcout": {
        "SCF": -2721.541435904716
    },
    "hf_lxygjos.qcout": {
        "SCF": -2724.0769973875713,
        "XYGJ-OS": -2726.3445157759393
    },
    "hf_mosmp2.qcout": {
        "MOS-MP2": -2725.302538779482,
        "SCF": -2721.541435904716
    },
    "hf_mp2.qcout": {
        "MP2": -2726.685661962005,
        "SCF": -2721.541435904716
    },
    "hf_pcm.qcout": {
        "SCF": -2720.703940318968
    },
    "hf_qcisd(t).qcout": {
        "QCISD": -2726.7853751012344,
        "QCISD(T)": -2726.8346541282745,
        "SCF": -2721.5414360843106
    },
    "hf_riccsd(t).qcout": {
        "CCSD": -2726.7641790658904,
        "CCSD(T)": -2726.829853468723,
        "MP2": -2726.6860802173014,
        "SCF": -2721.5414360843106
    },
    "hf_tpssh.qcout": {
        "SCF": -2732.938974944255
    },
    "hf_xyg3.qcout": {
        "SCF": -2728.769906036435,
        "XYG3": -2731.0640917605806
    },
    "hf_xygjos.qcout": {
        "SCF": -2724.0769973875713,
        "XYGJ-OS": -2726.3447230967517
    }
}'''
        ref_energies = json.loads(ref_energies_text)
        parsed_energies = dict()
        # noinspection PyUnresolvedReferences
        for filename in glob.glob(os.path.join(test_dir, "qchem_energies",
                                                         "*.qcout")):
            molname = os.path.basename(filename)
            qcout = QcOutput(filename)
            d = dict(qcout.data[0]["energies"])
            parsed_energies[molname] = d
        self.assertEqual(sorted(ref_energies.keys()),
                         sorted(parsed_energies.keys()))
        mols = sorted(ref_energies.keys())
        for molname in mols:
            self.assertEqual(sorted(ref_energies[molname].keys()),
                             sorted(parsed_energies[molname].keys()))
            methods = sorted(ref_energies[molname].keys())
            for method in methods:
                self.assertAlmostEqual(ref_energies[molname][method],
                                       parsed_energies[molname][method])

    def test_geom_opt(self):
        filename = os.path.join(test_dir, "thiophene_wfs_5_carboxyl.qcout")
        qcout = QcOutput(filename)
        self.assertEqual(qcout.data[0]["jobtype"], "opt")
        ans_energies = [('SCF', -20179.88483906483),
                        ('SCF', -20180.120269846386),
                        ('SCF', -20180.14892206486),
                        ('SCF', -20180.150026022537),
                        ('SCF', -20180.15020789526),
                        ('SCF', -20180.150206202714)]
        self.assertEqual(qcout.data[0]["energies"], ans_energies)
        ans_mol1 = '''Molecule Summary (H4 S1 C5 O2)
Reduced Formula: H4C5SO2
Charge = -1, Spin Mult = 2
Sites (12)
1 C     0.158839    -0.165379     0.000059
2 C    -0.520531    -1.366720     0.000349
3 C    -1.930811    -1.198460    -0.000041
4 C    -2.297971     0.127429    -0.000691
5 S    -0.938312     1.189630     0.000400
6 H    -0.014720    -2.325340     0.000549
7 H    -2.641720    -2.017721    -0.000161
8 H    -3.301032     0.535659    -0.001261
9 C     1.603079     0.076231    -0.000101
10 O     2.131988     1.173581    -0.000330
11 O     2.322109    -1.079218    -0.000021
12 H     3.262059    -0.820188    -0.000171'''
        ans_mol_last = '''Molecule Summary (H4 S1 C5 O2)
Reduced Formula: H4C5SO2
Charge = -1, Spin Mult = 2
Sites (12)
1 C     0.194695    -0.158362    -0.001887
2 C    -0.535373    -1.381241    -0.001073
3 C    -1.927071    -1.199274    -0.000052
4 C    -2.332651     0.131916     0.000329
5 S    -0.942111     1.224916    -0.001267
6 H    -0.038260    -2.345185    -0.001256
7 H    -2.636299    -2.025939     0.000620
8 H    -3.339756     0.529895     0.001288
9 C     1.579982     0.071245    -0.002733
10 O     2.196383     1.165675    -0.000178
11 O     2.352341    -1.114671     0.001634
12 H     3.261096    -0.769470     0.003158'''
        self.assertEqual(str(qcout.data[0]["molecules"][0]), ans_mol1)
        self.assertEqual(str(qcout.data[0]["molecules"][-1]), ans_mol_last)
        self.assertFalse(qcout.data[0]["has_error"])
        ans_gradient = [{'max_gradient': 0.07996,
                         'gradients': [(-0.0623076, -0.0157774, -2.05e-05),
                                       (0.0260287, 0.0289157, -6e-06),
                                       (-0.015738, 0.0103583, 1.87e-05),
                                       (0.0260219, -0.0028, -1.36e-05),
                                       (-0.0043158, -0.0245896, 2.83e-05),
                                       (4.8e-05, 0.000782, 1.3e-06),
                                       (0.0014679, 0.0020277, 3.9e-06),
                                       (0.0010437, -1.29e-05, -1.04e-05),
                                       (0.0799585, 0.0204159, 1e-06),
                                       (-0.0320357, -0.0421461, 2.1e-06),
                                       (-0.0237691, 0.0247526, -4.6e-06),
                                       (0.0035975, -0.0019264, -3e-07)],
                         'rms_gradient': 0.02244},
                        {'max_gradient': 0.02721,
                         'gradients': [(-0.0195677, -0.0008468, -3.2e-06),
                                       (0.0106798, 0.0039494, 1.11e-05),
                                       (-0.0086473, -0.0012624, -8.1e-06),
                                       (0.0065018, 0.0033749, 5e-07),
                                       (0.0002581, -0.0060831, 7.2e-06),
                                       (-0.0004373, -0.000504, 1.4e-06),
                                       (0.0003216, 0.0001059, -9e-07),
                                       (-0.000814, -5.03e-05, 3e-07),
                                       (0.0272109, 0.001408, -2.06e-05),
                                       (-0.0086971, -0.009251, 8.3e-06),
                                       (-0.0080925, 0.0112191, 2.9e-06),
                                       (0.0012838, -0.0020597, 1.1e-06)],
                         'rms_gradient': 0.007037},
                        {'max_gradient': 0.003444,
                         'gradients': [(0.0021606, 0.0013094, -1.68e-05),
                                       (0.0005757, -0.0002616, -1e-05),
                                       (2.73e-05, -0.0002868, 1.5e-05),
                                       (0.0001088, 0.0006944, -1.23e-05),
                                       (0.0006912, -0.0006523, 6.1e-06),
                                       (-0.0004191, -9.32e-05, -1.3e-06),
                                       (0.0002288, 3.98e-05, 1.8e-06),
                                       (-8.99e-05, -0.0002338, -3.2e-06),
                                       (1.95e-05, -0.0034439, 7.08e-05),
                                       (-0.0008228, -9.18e-05, -2.77e-05),
                                       (-0.0018054, 0.0034031, -2.21e-05),
                                       (-0.0006747, -0.0003834, -3e-07)],
                         'rms_gradient': 0.001008},
                        {'max_gradient': 0.002367,
                         'gradients': [(-0.0001646, 0.0006149, 4.17e-05),
                                       (-0.0004516, -0.0003116, 1.28e-05),
                                       (0.0003366, -3.27e-05, -1.59e-05),
                                       (-0.0003164, 0.0001775, 1.37e-05),
                                       (0.0001399, -0.0001201, -6.9e-06),
                                       (-0.0001374, -1.58e-05, 9e-07),
                                       (-1.19e-05, -3.93e-05, -3.3e-06),
                                       (-1.76e-05, -0.0001233, 5.1e-06),
                                       (9.73e-05, -0.0023668, -0.0001609),
                                       (0.0006998, 0.0009023, 6.31e-05),
                                       (-0.0002169, 0.0014874, 4.95e-05),
                                       (4.28e-05, -0.0001724, 2e-07)],
                         'rms_gradient': 0.0005339},
                        {'max_gradient': 0.001246,
                         'gradients': [(-6.88e-05, 0.0001757, -8.32e-05),
                                       (-0.0002264, -0.0001306, -1.93e-05),
                                       (0.0001526, -1.39e-05, 2.05e-05),
                                       (-0.0001401, 3.8e-06, -2.05e-05),
                                       (1.52e-05, 0.0001152, 8e-06),
                                       (2.01e-05, -3.69e-05, -1e-06),
                                       (-3.62e-05, -3.51e-05, 5.5e-06),
                                       (1.01e-05, -1.23e-05, -6.8e-06),
                                       (9.73e-05, -0.0012462, 0.0003246),
                                       (0.0003926, 0.0008331, -0.0001269),
                                       (-0.0002294, 0.000281, -0.0001009),
                                       (1.3e-05, 6.61e-05, 0.0)],
                         'rms_gradient': 0.0002814},
                        {'max_gradient': 0.0006359,
                         'gradients': [(0.0001036, -0.0001339, 0.0001633),
                                       (0.0001003, 6.98e-05, 3.43e-05),
                                       (-8.28e-05, 1.1e-05, -3.31e-05),
                                       (6.2e-05, -0.0001068, 3.41e-05),
                                       (-5.02e-05, 0.0001346, -1.18e-05),
                                       (8.72e-05, -7.3e-06, 1.5e-06),
                                       (-1.7e-05, 4.9e-06, -1.05e-05),
                                       (1.29e-05, 5.9e-05, 1.26e-05),
                                       (-0.0001059, -5.4e-06, -0.0006359),
                                       (-1.48e-05, 0.0002152, 0.0002469),
                                       (-0.0001335, -0.0003534, 0.0001988),
                                       (3.83e-05, 0.0001124, -1e-07)],
                         'rms_gradient': 0.0001535}]
        self.assertEqual(qcout.data[0]["gradients"], ans_gradient)
        ans_inp = '''$molecule
 -1  2
 C           0.15884000       -0.16538000        0.00006000
 C          -0.52053000       -1.36672000        0.00035000
 C          -1.93081000       -1.19846000       -0.00004000
 C          -2.29797000        0.12743000       -0.00069000
 S          -0.93831000        1.18963000        0.00040000
 H          -0.01472000       -2.32534000        0.00055000
 H          -2.64172000       -2.01772000       -0.00016000
 H          -3.30103000        0.53566000       -0.00126000
 C           1.60308000        0.07623000       -0.00010000
 O           2.13199000        1.17358000       -0.00033000
 O           2.32211000       -1.07922000       -0.00002000
 H           3.26206000       -0.82019000       -0.00017000
$end


$rem
   jobtype = opt
  exchange = b3lyp
     basis = 6-31+g*
$end

'''
        self.assertEqual(str(qcout.data[0]['input']), ans_inp)
        self.assertTrue(qcout.data[0]['gracefully_terminated'])
        ans_scf_iter = [[(-743.3130310589, 0.0561),
                         (-741.3557302205, 0.00841),
                         (-740.7031048846, 0.0157),
                         (-741.5589873953, 0.00303),
                         (-741.5918010434, 0.00118),
                         (-741.5966923809, 0.000332),
                         (-741.5970287119, 0.000158),
                         (-741.5971282029, 4.38e-05),
                         (-741.5971448077, 2.17e-05),
                         (-741.5971501973, 7.7e-06),
                         (-741.5971533576, 5.05e-06),
                         (-741.5971541122, 2.7e-06),
                         (-741.5971544119, 9.48e-07),
                         (-741.5971544408, 2.61e-07),
                         (-741.5971544436, 1.21e-07),
                         (-741.5971544441, 5.45e-08),
                         (-741.5971544442, 1.77e-08),
                         (-741.5971544442, 7.79e-09)],
                        [(-741.5552794274, 0.00265),
                         (-741.6048574279, 0.000515),
                         (-741.6037290502, 0.000807),
                         (-741.6056978336, 0.000188),
                         (-741.6057976553, 4.78e-05),
                         (-741.6058045572, 1.54e-05),
                         (-741.6058057373, 4.51e-06),
                         (-741.6058061671, 2.91e-06),
                         (-741.6058062822, 8.32e-07),
                         (-741.6058063435, 7.17e-07),
                         (-741.6058063636, 1.97e-07),
                         (-741.6058063662, 5.03e-08),
                         (-741.6058063666, 3.35e-08),
                         (-741.6058063666, 1.24e-08),
                         (-741.6058063666, 5.25e-09)],
                        [(-741.6023833754, 0.0013),
                         (-741.6065067966, 0.000305),
                         (-741.6057886337, 0.000559),
                         (-741.6068434004, 7.61e-05),
                         (-741.6068555361, 3.4e-05),
                         (-741.6068589376, 5.66e-06),
                         (-741.6068591778, 2.95e-06),
                         (-741.60685927, 1.27e-06),
                         (-741.6068592962, 4.82e-07),
                         (-741.6068593106, 3.84e-07),
                         (-741.6068593157, 9.23e-08),
                         (-741.6068593162, 2.49e-08),
                         (-741.6068593163, 1.52e-08),
                         (-741.6068593163, 5.71e-09)],
                        [(-741.6012175391, 0.000209),
                         (-741.6068794773, 7.2e-05),
                         (-741.606851035, 0.000117),
                         (-741.606899078, 1.53e-05),
                         (-741.6068997567, 6.01e-06),
                         (-741.6068998747, 1.68e-06),
                         (-741.6068998849, 5.32e-07),
                         (-741.6068998857, 2.76e-07),
                         (-741.606899886, 6.41e-08),
                         (-741.606899886, 3.08e-08),
                         (-741.606899886, 9.5e-09)],
                        [(-741.6067290885, 0.0001),
                         (-741.6069044268, 2.64e-05),
                         (-741.6068991026, 5.29e-05),
                         (-741.6069065234, 3.51e-06),
                         (-741.6069065452, 2.49e-06),
                         (-741.6069065686, 3.57e-07),
                         (-741.6069065693, 2.59e-07),
                         (-741.6069065696, 7.05e-08),
                         (-741.6069065696, 4.44e-08),
                         (-741.6069065697, 1.52e-08),
                         (-741.6069065697, 8.17e-09)],
                        [(-741.6074251344, 0.000129),
                         (-741.6069044127, 2.43e-05),
                         (-741.6068998551, 4.95e-05),
                         (-741.6069064294, 4.49e-06),
                         (-741.606906478, 2.77e-06),
                         (-741.6069065049, 5.85e-07),
                         (-741.6069065068, 2.74e-07),
                         (-741.6069065073, 6.99e-08),
                         (-741.6069065074, 3.37e-08),
                         (-741.6069065075, 1.89e-08),
                         (-741.6069065075, 7.38e-09)]]
        self.assertEqual(qcout.data[0]['scf_iteration_energies'], ans_scf_iter)

    def test_multiple_step_job(self):
        filename = os.path.join(test_dir, "CdBr2.qcout")
        qcout = QcOutput(filename)
        self.assertEqual(len(qcout.data), 3)
        self.assertEqual(qcout.data[0]['jobtype'], 'opt')
        self.assertEqual(qcout.data[1]['jobtype'], 'freq')
        ans_thermo_corr_text = '''
{
    "Rotational Enthalpy": 0.025714259,
    "Rotational Entropy": 0.000833523586,
    "Total Enthalpy": 0.199729978,
    "Total Entropy": 0.003218965579,
    "Translational Enthalpy": 0.038549707,
    "Translational Entropy": 0.001851513374,
    "Vibrational Enthalpy": 0.109795116,
    "Vibrational Entropy": 0.000533928619,
    "ZPE": 0.039330241,
    "Zero point vibrational energy": 0.039330241,
    "gas constant (RT)": 0.025714259
}'''
        ans_thermo_corr = json.loads(ans_thermo_corr_text)
        self.assertEqual(sorted(qcout.data[1]['corrections'].keys()),
                         sorted(ans_thermo_corr.keys()))
        for k, ref in ans_thermo_corr.iteritems():
            self.assertAlmostEqual(qcout.data[1]['corrections'][k], ref)
        self.assertEqual(len(qcout.data[1]['molecules']), 1)
        ans_mol1 = '''Molecule Summary (Br2 Cd1)
Reduced Formula: CdBr2
Charge = 0, Spin Mult = 1
Sites (3)
1 Br     0.000000     0.000000    -2.453720
2 Cd     0.000000     0.000000     0.000000
3 Br     0.000000     0.000000     2.453720'''
        self.assertEqual(str(qcout.data[1]['molecules'][0]), ans_mol1)
        self.assertFalse(qcout.data[1]['has_error'])
        self.assertEqual(qcout.data[1]['gradients'], [])
        ans_inp = '''$molecule
 read
$end


$rem
         jobtype = freq
        exchange = b3lyp
           basis = gen
             ecp = gen
  max_scf_cycles = 100
       scf_guess = gwh
$end


$basis
 Br
 srlc
 ****
 Cd
 srsc
 ****
$end


$ecp
 Br
 srlc
 ****
 Cd
 srsc
 ****
$end

'''
        self.assertEqual(str(qcout.data[1]['input']), ans_inp)
        ans_freq = [{'vib_mode:': ((0.17, -0.475, 0.0),
                                   (-0.236, 0.659, 0.0),
                                   (0.17, -0.475, 0.0)),
                     'frequency:': 61.36},
                    {'vib_mode:': ((-0.475, -0.17, 0.0),
                                   (0.659, 0.236, 0.0),
                                   (-0.475, -0.17, 0.0)),
                     'frequency:': 61.36},
                    {'vib_mode:': ((0.0, 0.0, 0.707),
                                   (0.0, 0.0, 0.0),
                                   (0.0, 0.0, -0.707)),
                     'frequency:': 199.94},
                    {'vib_mode:': ((0.17, -0.475, 0.0),
                                   (-0.236, 0.659, 0.0),
                                   (0.17, -0.475, 0.0),
                                   (0.0, 0.0, -0.505),
                                   (0.0, 0.0, 0.7),
                                   (0.0, 0.0, -0.505)),
                     'frequency:': 311.74}]
        self.assertEqual(qcout.data[1]['frequencies'], ans_freq)
        self.assertEqual(qcout.data[2]['energies'],
                         [('SCF', -5296.720321211475)])
        ans_scf_iter_ene = [[(-176.9147092199, 0.779),
                             (-156.8236033975, 0.115),
                             (-152.9396694452, 0.157),
                             (-183.2743425778, 0.138),
                             (-182.2994943574, 0.142),
                             (-181.990425533, 0.143),
                             (-182.1690180647, 0.142),
                             (-106.6454708618, 0.239),
                             (-193.8056267625, 0.0432),
                             (-193.0854096948, 0.0455),
                             (-194.6340538334, 0.0062),
                             (-194.6495072245, 0.00205),
                             (-194.6508787796, 0.000189),
                             (-194.6508984743, 2.18e-05),
                             (-194.6508986262, 2.17e-06)]]
        self.assertEqual(qcout.data[2]['scf_iteration_energies'],
                         ans_scf_iter_ene)

    def test_failed_message(self):
        scf_file = os.path.join(test_dir, "hf.qcout")
        scf_qcout = QcOutput(scf_file)
        self.assertTrue(scf_qcout.data[0]['has_error'])
        self.assertEqual(scf_qcout.data[0]['errors'],
                         ['Bad SCF convergence',
                          'Molecular charge is not found'])
        geom_file = os.path.join(test_dir, "hf_opt_failed.qcout")
        geom_qcout = QcOutput(geom_file)
        self.assertTrue(geom_qcout.data[0]['has_error'])
        self.assertEqual(geom_qcout.data[0]['errors'],
                         ['Geometry optimization failed'])


if __name__ == "__main__":
    unittest.main()