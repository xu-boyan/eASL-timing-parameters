import streamlit as st
import math
import pandas as pd

def linear_PLDs(cv4, cv5, cv6):
    ld = cv5 / cv6
    plds = [cv4 + ld*i for i in range(cv6)]
    lds = [ld] * cv6
    return (lds, plds)


def exponential_PLDs(cv4, cv5, cv6):
    t1a = 1650  # T1 of arterial blood at 3T
    Stot = (1-math.exp(-cv5 / t1a)) * math.exp(-cv4 / t1a)
    Starget = Stot / cv6

    plds = []
    lds = []
    pld = cv4
    for i in range(cv6):
        ld = - t1a * math.log(1-Starget * math.exp(pld/t1a))
        lds.append(ld)
        plds.append(pld)
        # next pld
        pld = pld + ld

    return (lds, plds)


def ge_asl_pld(cv4, cv5, cv6, cv7):
    (lds_lin, plds_lin) = linear_PLDs(cv4, cv5, cv6)
    (lds_exp, plds_exp) = exponential_PLDs(cv4, cv5, cv6)

    lds = [cv7*ld_lin + (1-cv7)*ld_exp for (ld_lin, ld_exp) in zip(lds_lin, lds_exp)]
    plds = [cv7*pld_lin + (1-cv7)*pld_exp for (pld_lin, pld_exp) in zip(plds_lin, plds_exp)]

    print("Below are the combinations of ld and pld:")
    for ld, pld in zip(lds, plds):
        print((ld,pld))
    return (lds, plds)



st.title("⏱️ GE multi-PLD ASL timing parameters")
st.markdown("""
Multi-PLD ASL are acquired using time-encoded method. 
Upon successful scanning, the system automatically generates decoded RAW images 
(with series number calculated as the actual scanning series number multiplied by 100).
This RAW images contains multiple 3D images in the following order:

- Perfusion-weighted images for each individual PLD (with specific LD & PLD values calculated by this program)
- A combined perfusion-weighted image (uses the entire label duration, CV5, and the shortest post label delay, CV4)
- Reference images

""")
st.markdown("---")
cv4 = st.number_input("CV4: Post label delay time (e.g. 1000; minimum: 700; maximum 4000)", value=1000)
cv5 = st.number_input("CV5: Perfusion labeling time (e.g. 3500; minimum: 0; maximum 4000)", value=3500)
cv6 = st.selectbox("CV6: Number of post label delay images to acquire (e.g. 7)", options=[3, 7])
cv7 = st.number_input("CV7: Delay linearity (e.g. 0.5; minimum: 0.0; maximum: 1.0)", value=0.5)

if st.button("🚀 calculate"):
    try:
        [lds, plds] = ge_asl_pld(cv4, cv5, cv6, cv7)
        df = pd.DataFrame(
            {
                "labeling time (ms)": lds,
                "post labeling delay (ms)": plds
            }
        )
        st.markdown("---")
        st.subheader("results")
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "labeling time (ms)": st.column_config.NumberColumn(
                    format="%.2f",
                    help="labeling time (ms)"
                ),
                "post labeling delay (ms)": st.column_config.NumberColumn(
                    format="%.2f",
                    help="post labeling time (ms)"
                )
            }
        )
    except Exception as e:
        st.error(f"Error: {str(e)}")

st.markdown("---")
st.caption("Xu Boyan | MR Research China, GE Healthcare")

