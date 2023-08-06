from skewt import SkewT
from matplotlib.pyplot import show

# Do the examples in the "examples" directory
examples=("2013070200","2013070900",)
parcels=((1004.,17.4,8.6),(1033.,10.7,-0.9),)

for ex,pc in zip(examples,parcels):
    sounding=SkewT.Sounding("./examples/94975.%s.txt"%ex)
    sounding.make_skewt_axes()
    sounding.add_profile(color='r',lw=2)
    sounding.lift_parcel(*pc)
    sounding.column_diagnostics()
    sounding.fig.savefig("./examples/94975.%s.png"%ex)

show()

