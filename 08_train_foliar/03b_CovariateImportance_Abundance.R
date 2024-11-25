# ---------------------------------------------------------------------------
# Plot covariate importances
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2024-09-26
# Usage: Script should be executed in R 4.1.0+.
# Description: "Plot covariate importances" plots the covariate importances from 10 outer cross validation iterations.
# ---------------------------------------------------------------------------

# Import libraries
library(dplyr)
library(fs)
library(ggplot2)
library(ggtext)
library(RColorBrewer)
library(tibble)
library(tidyr)

# Set round date
round_date = 'round_20241121'

# Define species
group = 'alnus'

# Set root directory
drive = 'D:'
root_folder = 'ACCS_Work/Projects/VegetationEcology/AKVEG_Map/Data'

# Define folder structure
target_folder = path(drive, root_folder, 'Data_Output/model_results/', round_date, group)

# Define input data
importance_input = path(target_folder, paste(group, '_importances.csv', sep = ''))

# Define output files
importance_output = path(target_folder, paste(group, '_importance.jpg', sep = ''))

# Process classifier importances
classifier_data = read.csv(importance_input) %>%
  filter(component == 'classifier') %>%
  mutate(covariate = paste(' ', covariate, sep = '')) %>%
  group_by(covariate) %>%
  summarize(importance_mean = mean(importance),
            importance_std = sd(importance)) %>%
  mutate(imp_rel_mean = importance_mean / max(.['importance_mean']),
         imp_rel_std = importance_std / max(.['importance_mean'])) %>%
  arrange(desc(imp_rel_mean)) %>%
  mutate(Component = 'classifier')

# Process regressor importances
regressor_data = read.csv(importance_input) %>%
  filter(component == 'regressor') %>%
  mutate(covariate = paste(' ', covariate, sep = '')) %>%
  group_by(covariate) %>%
  summarize(importance_mean = mean(importance),
            importance_std = sd(importance)) %>%
  mutate(imp_rel_mean = importance_mean / max(.['importance_mean']),
         imp_rel_std = importance_std / max(.['importance_mean'])) %>%
  arrange(desc(imp_rel_mean)) %>%
  mutate(Component = 'regressor')

# Combine data
importance_data = rbind(classifier_data[1:10,], regressor_data[1:10,])

# Plot classifier importance
importance_plot = ggplot(importance_data, aes(x=reorder(covariate, -imp_rel_mean), y=imp_rel_mean, color=Component, fill=Component)) +
  geom_bar(stat='identity', alpha=0.7, width=0.8) +
  geom_linerange(aes(ymin=imp_rel_mean - imp_rel_std,
                     ymax=imp_rel_mean + imp_rel_std), color='#000000') +
  theme_minimal() +
  labs(y = 'Relative covariate importance (top 10)') +
  theme(axis.title.x = element_blank(),
        axis.text.x = element_markdown(angle = 45, vjust = 1, hjust = 1)) +
  scale_fill_manual(values = c("#36648B", "#53868B")) +
  scale_color_manual(values = c('#36648B', '#53868B'))

# Export plot
ggsave(importance_output,
       plot = importance_plot,
       device = 'jpeg',
       path = NULL,
       scale = 1,
       width = 6.5,
       height = 3.5,
       units = 'in',
       dpi = 600,
       limitsize = TRUE)