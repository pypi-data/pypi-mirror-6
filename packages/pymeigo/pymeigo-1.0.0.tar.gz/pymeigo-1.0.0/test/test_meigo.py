from pymeigo import ESS, rosen_for_r, VNS, MEIGO


def test_meigo_ESS():
    m = ESS(f=rosen_for_r)
    print m
    m.run(x_U=[2,2], x_L=[-1,-1])
    m.plot()
    print m


def test_meigo_VNS():
    m = VNS(f=rosen_for_r)
    print m
    m.run(x_U=[2,2], x_L=[-1,-1])
    m.plot()


def test_meigo():
    m = MEIGO("ESS", f=rosen_for_r)
    m.run(x_U=[2,2], x_L=[-1,-1])
    m.plot()


