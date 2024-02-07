
# changesubjectmarkers: Perform statistical analysis of change between proto and modern forms of person markers.
# Copyright (C) 2024  Peter Dekker, Sonja Gipper, Bart de Boer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Input data expected to be in: data/verbal_person-number_indexes_merged.csv
# See README for more information on installation.

import pandas as pd
import editdistance
import seaborn as sns
import matplotlib.pyplot as plt
import os
import unidecode
import numpy as np
# from itertools import combinations

import rpy2.robjects as robjects
import rpy2.robjects.numpy2ri
import rpy2.robjects.pandas2ri
robjects.numpy2ri.activate()
robjects.pandas2ri.activate()

### User-settable params: ###
NORMALISATION = "none" #For unnormalised model: 'none'. For normalised model: 'max'
EXCLUDE_LANGUAGES_PROTO_0 = False # Exclude languages (and thus whole families) where one of the protoforms is zero
### ###

plt.rcParams['savefig.dpi'] = 300
currentdir = os.path.dirname(os.path.realpath(__file__))
OUTPUT_DIR = "output_data"
OUTPUT_DIR_PROTO = os.path.join(OUTPUT_DIR, "proto")
excl_proto0_label = "_exclproto0" if EXCLUDE_LANGUAGES_PROTO_0 else ""
norm_label = f"_{NORMALISATION}"
NORM_STRING_TITLE = "normalised " if NORMALISATION != "none" else "" # This assumes always 'max' normalisation, other types get the same label
pd.set_option('display.max_rows', 100)
img_extension_pyplots = "png"
person_markers = ["1sg", "2sg", "3sg", "1pl", "2pl", "3pl"]


def normalised_levenshtein(modern,proto, norm):
    raw_dist = editdistance.eval(modern, proto)
    if norm == "mean":
        norm_len = np.mean([len(modern),len(proto)])
    elif norm == "max":
        norm_len = max(len(modern), len(proto))
    elif norm=="sqrt":
        norm_len = np.sqrt(np.mean([len(modern),len(proto)]))
    elif norm=="none":
        norm_len = 1
    else:
        raise ValueError("norm should be one of 'mean' or 'max'.")
    return raw_dist / norm_len if norm_len > 0 else 0


def get_first(x):
    return x[0]

def stats_df(df, label):
    n_entries = len(df)
    n_languages = df["language"].nunique()
    n_proto_languages = df["proto_language"].nunique()
    # nunique_family = df.groupby("proto_language")["language"].nunique()
    print(f"{label}: entries: {n_entries}, languages: {n_languages}, proto_languages: {n_proto_languages}")

def main():

    if not os.path.exists(OUTPUT_DIR_PROTO):
        os.makedirs(OUTPUT_DIR_PROTO)

    df = pd.read_csv("data/verbal_person-number_indexes_merged.csv")


    # Reporting: Create an excerpt of Serzant & Moroz (2022) data (for SI)
    df[["language", "proto_language", "person_number", "person", "number", "modern_form", "proto_form", "clade3"]].head(18).to_latex(os.path.join(OUTPUT_DIR,"excerpt_serzantmoroz2022.tex"))


    df = df.drop(columns=["source", "comment", "proto_source", "proto_comments", "changed_GM"])
    stats_df(df, "original")
    # Filter out entries without form or protoform (removes languages without protolanguage + possibly more)
    df = df[df['modern_form'].notna()]
    stats_df(df, "after removing modern forms which are NA")
    df = df[df['proto_form'].notna()]
    #languages_one_protoform_na = df[df["proto_form"].isna()][["language"]]
    #df = df[~df["language"].isin(languages_one_protoform_na["language"])]
    stats_df(df, "after removing languages with protoform NA")

    # Reporting: Creating tables with zero forms, to aid discussion in paper
    proto_lengths = df.groupby(["proto_language","person_number"]).first()["proto_length"]
    proto_lengths.to_csv(os.path.join(OUTPUT_DIR,"proto_lengths_fam.csv"))
    proto_lengths_zero = proto_lengths[proto_lengths == 0.0]
    proto_lengths_zero.to_csv(os.path.join(OUTPUT_DIR,"proto_lengths_fam_zero.csv"))
    modern_reflexes_proto_lengths_zero = pd.merge(df, proto_lengths_zero, on=["proto_language", "person_number"])
    modern_reflexes_proto_lengths_zero.to_csv(os.path.join(OUTPUT_DIR,"modern_reflexes_proto_zero.csv"))


    # Find languages which have both protoform and modern form with length 0
    if EXCLUDE_LANGUAGES_PROTO_0:
        #languages_00 = df[(df["modern_length"]==0.0) & (df["proto_length"]==0.0)][["language","proto_language"]]
        languages_proto0 = df[df["proto_length"]==0.0][["language"]]
        df = df[~df["language"].isin(languages_proto0["language"])] # remove all languages where protolanguage is 0
        stats_df(df, "after removing languages where one protoform has length 0")

    
    ### Analysis levenshtein distance in forms

    for form_type in ["modern_form", "proto_form"]:
        ## Split alternative forms based on delimiters , and /, and take first
        df[f"{form_type}_corr"] = df[form_type].str.split(",|/").apply(get_first)
        
        ## Delete parts in brackets
        # Possible future: Create alternative forms based on letters in brackets os(i)
        #brackets = df[f"{form_type}_corr"].str.contains("\(.+\)")
        # print(brackets.value_counts())
        df[f"{form_type}_corr"] = df[f"{form_type}_corr"].str.replace("\(.+\)", "", regex=True)

        ## Delete dashes
        df[f"{form_type}_corr"] = df[f"{form_type}_corr"].str.replace("-", "", regex=False)
        ## Delete ... (non-concatenative morphology)
        df[f"{form_type}_corr"] = df[f"{form_type}_corr"].str.replace("...", "", regex=False)
        df[f"{form_type}_corr"] = df[f"{form_type}_corr"].str.replace("…", "", regex=False)
        ## Delete 2 (from h2)
        df[f"{form_type}_corr"] = df[f"{form_type}_corr"].str.replace("2", "", regex=False)
        ## Delete 0 (empty person marker is just represented by empty string)
        df[f"{form_type}_corr"] = df[f"{form_type}_corr"].str.replace("0", "", regex=False)
        ## Delete ø (empty person marker is just represented by empty string)
        df[f"{form_type}_corr"] = df[f"{form_type}_corr"].str.replace("ø", "", regex=False)
        ## Delete *
        df[f"{form_type}_corr"] = df[f"{form_type}_corr"].str.replace("*", "", regex=False)
        ## Delete ´ ' # (segments which are not counted in precalculated length)
        df[f"{form_type}_corr"] = df[f"{form_type}_corr"].str.replace("[´`'#]", "", regex=True)
        ## Delete : (lengthening vowel but no sound on its own)
        df[f"{form_type}_corr"] = df[f"{form_type}_corr"].str.replace(":", "", regex=False)
        
        df[f"{form_type}_corr"] = df[f"{form_type}_corr"].apply(unidecode.unidecode)

    df["proto_levenshtein"] = df.apply(lambda x: normalised_levenshtein(x["modern_form_corr"], x["proto_form_corr"], NORMALISATION), axis=1)

    # From now on df not further mutated
    # Output final dataframe for statistical analysis to file
    df.to_csv("final_data_cleaned_for_analysis.csv")

    ## Reporting: calculate proportion of forms with Levenshtein distance 0 that also have protoform 0
    print("Distribution of persons in dataset")
    distr_persons_dataset = df["person_number"].value_counts()
    distr_persons_dataset.to_latex(os.path.join(OUTPUT_DIR,"distr_persons_dataset.tex"))
    print(distr_persons_dataset)

    print("Distribution of proto lengths in all data:")
    distr_proto_dataset = df["proto_length"].value_counts()
    distr_proto_dataset.to_latex(os.path.join(OUTPUT_DIR,"distr_proto_dataset.tex"))
    print(distr_proto_dataset)

    print("Distribution of persons where protoform is empty")
    distr_persons_proto0 = df[df["proto_length"]==0.0]["person_number"].value_counts()
    distr_persons_proto0.to_latex(os.path.join(OUTPUT_DIR,"distr_persons_proto0.tex"))
    print(distr_persons_proto0)

    df_levenshtein0 = df[df["proto_levenshtein"]==0.0]
    print(f"Entries with Levenshtein 0: {len(df_levenshtein0)} (total entries: {len(df)})")
    print("Distribution of proto lengths in entries with Levenshtein 0:")
    distr_proto_lev0 = df_levenshtein0["proto_length"].value_counts()
    distr_proto_lev0.to_latex(os.path.join(OUTPUT_DIR,"distr_proto_lev0.tex"))
    print(distr_proto_lev0)

    print("Distribution of persons, of entries with Levenshtein 0, and where protoform is empty")
    distr_persons_lev0_proto0 = df_levenshtein0[df_levenshtein0["proto_length"]==0.0]["person_number"].value_counts()
    print(distr_persons_lev0_proto0)
    distr_persons_lev0_proto0.to_latex(os.path.join(OUTPUT_DIR,"distr_persons_lev0_proto0.tex"))
    


    ## Statistical analyses in R
    with robjects.local_context() as lc:
        lc['df'] = df


        robjects.r(f'''
                library(tidyverse)
                library(lme4)
                library(ggeffects)
                library(afex)
                df <- mutate(df,
                            number = relevel(factor(number), ref = 'sg'))

                modelProtoLev <- lmer(proto_levenshtein ~ person*number + (1|clade3), data=df)
                modelProtoLevSum <- summary(modelProtoLev)
                predictionsProtoLev <- ggpredict(model=modelProtoLev, terms=c("person", "number"))
                plot(predictionsProtoLev)+
                ggtitle("Mixed model {NORM_STRING_TITLE}Levenshtein distance proto and modern length")+
                labs(y = "Levenshtein distance")
                ggsave("{OUTPUT_DIR_PROTO}/predictions_proto_levenshtein{excl_proto0_label}{norm_label}.png", bg = "white")
                ggsave("{OUTPUT_DIR_PROTO}/predictions_proto_levenshtein{excl_proto0_label}{norm_label}.pdf", bg = "white")

                # ANOVA test
                anovaLevAfex <- mixed(proto_levenshtein ~ person*number + (1|clade3), data=df, method='LRT')

                ''')

        print(" - Proto Levenshtein")
        print(lc['modelProtoLev'])
        print(lc['modelProtoLevSum'])
        print(lc['predictionsProtoLev'])


        print(" - Anova afex")
        print(lc['anovaLevAfex'])

    # sns.violinplot(x="person_number", y="proto_levenshtein", data=df) # hue="proto_language"
    # plt.savefig(os.path.join(OUTPUT_DIR_PROTO,f"proto_levenshtein_violin{excl_proto0_label}{norm_label}.{img_extension_pyplots}"))
    # plt.clf()
    # sns.stripplot(x="person_number", y="proto_levenshtein", data=df)
    # plt.savefig(os.path.join(OUTPUT_DIR_PROTO,f"proto_levenshtein_strip{excl_proto0_label}{norm_label}.{img_extension_pyplots}"))
    # plt.clf()


if __name__ == "__main__":
    main()
    