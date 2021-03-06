conddb_import -f sqlite_file:norm_ecaltemplates_popcon_runs_271983_272818.db  -i EcalPulseShapes_data -c sqlite_file:norm_ecaltemplates_popcon_2016_calib.db -t EcalPulseShapes_data -b 271983
conddb_import -f sqlite_file:norm_ecaltemplates_popcon_runs_273301_273590.db  -i EcalPulseShapes_data -c sqlite_file:norm_ecaltemplates_popcon_2016_calib.db -t EcalPulseShapes_data -b 272818
conddb_import -f sqlite_file:norm_ecaltemplates_popcon_runs_274080_274344.db  -i EcalPulseShapes_data -c sqlite_file:norm_ecaltemplates_popcon_2016_calib.db -t EcalPulseShapes_data -b 274080
conddb_import -f sqlite_file:norm_ecaltemplates_popcon_runs_274958_275659.db  -i EcalPulseShapes_data -c sqlite_file:norm_ecaltemplates_popcon_2016_calib.db -t EcalPulseShapes_data -b 274958
conddb_import -f sqlite_file:norm_ecaltemplates_popcon_runs_275757_275931.db  -i EcalPulseShapes_data -c sqlite_file:norm_ecaltemplates_popcon_2016_calib.db -t EcalPulseShapes_data -b 275757
conddb_import -f sqlite_file:norm_ecaltemplates_popcon_runs_276315_276587.db  -i EcalPulseShapes_data -c sqlite_file:norm_ecaltemplates_popcon_2016_calib.db -t EcalPulseShapes_data -b 276315
conddb_import -f sqlite_file:norm_ecaltemplates_popcon_runs_277932_277992.db  -i EcalPulseShapes_data -c sqlite_file:norm_ecaltemplates_popcon_2016_calib.db -t EcalPulseShapes_data -b 277932
conddb_import -f sqlite_file:norm_ecaltemplates_popcon_runs_278969_278976.db  -i EcalPulseShapes_data -c sqlite_file:norm_ecaltemplates_popcon_2016_calib.db -t EcalPulseShapes_data -b 278346
conddb_import -f sqlite_file:norm_ecaltemplates_popcon_runs_279115_279116.db  -i EcalPulseShapes_data -c sqlite_file:norm_ecaltemplates_popcon_2016_calib.db -t EcalPulseShapes_data -b 278977
conddb_import -f sqlite_file:norm_ecaltemplates_popcon_runs_279653_279658.db  -i EcalPulseShapes_data -c sqlite_file:norm_ecaltemplates_popcon_2016_calib.db -t EcalPulseShapes_data -b 279474
conddb_import -f sqlite_file:norm_ecaltemplates_popcon_runs_279841_279841.db  -i EcalPulseShapes_data -c sqlite_file:norm_ecaltemplates_popcon_2016_calib.db -t EcalPulseShapes_data -b 279717
conddb_import -f sqlite_file:norm_ecaltemplates_popcon_runs_281616_282092.db  -i EcalPulseShapes_data -c sqlite_file:norm_ecaltemplates_popcon_2016_calib.db -t EcalPulseShapes_data -b 281010
conddb_import -f sqlite_file:norm_ecaltemplates_popcon_runs_282408_283067.db  -i EcalPulseShapes_data -c sqlite_file:norm_ecaltemplates_popcon_2016_calib.db -t EcalPulseShapes_data -b 282408
conddb_import -f sqlite_file:norm_ecaltemplates_popcon_runs_283171_283835.db  -i EcalPulseShapes_data -c sqlite_file:norm_ecaltemplates_popcon_2016_calib.db -t EcalPulseShapes_data -b 283171
conddb_import -f sqlite_file:norm_ecaltemplates_popcon_runs_283863_284035.db  -i EcalPulseShapes_data -c sqlite_file:norm_ecaltemplates_popcon_2016_calib.db -t EcalPulseShapes_data -b 283863

echo "===> Now checking the contents..."
conddb --db norm_ecaltemplates_popcon_2016_calib.db list EcalPulseShapes_data
