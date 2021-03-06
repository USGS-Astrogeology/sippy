import bundle
ibun = bundle.Isis.BundleObservationSolveSettings
from enum import Enum

instrument_pointing_lookup = {0: 'NoPointingFactors',
                              1: 'AnglesOnly',
                              2: 'AnglesVelocity',
                              3: 'AnglesVelocityAcceleration',
                              4: 'AllPointingCoefficients'}

instrument_position_lookup = {0: 'NoPositionFactors',
                              1: 'PositionOnly',
                              2: 'PositionVelocity',
                              3: 'PositionVelocityAcceleration',
                              4: 'AllPositionCoefficients'}

print('reloaded')

class BundleAdjust():

    def __init__(self, settings={}):
        """
        Create a bundle adjustment
        """
        self._bwrapper = bundle.Isis
        self.settings = self._bwrapper.BundleSettings()
        self.obs_settings = self._bwrapper.BundleObservationSolveSettings()
        self.set_solve_options(settings)

    @property
    def observation_mode(self):
        return self.settings.solveObservationMode()

    @observation_mode.setter
    def observation_mode(self, val):
        self.settings.setSolveOptions(solveObservationMode=val)

    @property
    def update_cube_labels(self):
        return self.settings.updateCubeLabel()

    @update_cube_labels.setter
    def update_cube_labels(self, val):
        self.settings.setSolveOptions(updateCubeLabel=val)

    @property
    def error_propagation(self):
        return self.settings.errorPropagation()

    @error_propagation.setter
    def error_propagation(self, val):
        self.settings.setSolveOptions(errorPropagation=val)

    @property
    def solve_for_radius(self):
        return self.settings.solveRadius()

    @solve_for_radius.setter
    def solve_for_radius(self, val):
        self.settings.setSolveOptions(solveRadius=val)

    @property
    def global_apriori_lat_sigma(self):
        return self.settings.globalLatitudeAprioriSigma()

    @global_apriori_lat_sigma.setter
    def global_apriori_lat_sigma(self, val):
        self.settings.setSolveOptions(globalLatitudeAprioriSigma=val)

    @property
    def global_apriori_lon_sigma(self):
        return self.settings.globalLongitudeAprioriSigma()

    @global_apriori_lon_sigma.setter
    def global_apriori_lon_sigma(self, val):
        self.settings.setSolveOptions(globalLongitudeAprioriSigma=val)

    @property
    def global_apriori_radius_sigma(self):
        return self.settings.globalRadiusAprioriSigma()

    @global_apriori_radius_sigma.setter
    def global_apriori_radius_sigma(self, val):
        self.settings.setSolveOptions(globalRadiusAprioriSigma=val)

    @property
    def outlier_rejection(self):
        return self.settings.outlierRejection()

    @outlier_rejection.setter
    def outlier_rejection(self, val):
        self.settings.setOutlierRejection(val)

    @property
    def outlier_rejection_multiplier(self):
        return self.settings.outlierRejectionMultiplier()

    @outlier_rejection_multiplier.setter
    def outlier_rejection_multiplier(self, val):
        self.settings.setOutlierRejection(self.outlier_rejection, val)

    @property
    def solve_for_twist(self):
        if not hasattr(self, '_twist'):
            self._twist = True
        return self._twist

    @solve_for_twist.setter
    def solve_for_twist(self, val):
        self._solve_for_twist = val

    @property
    def instrument_pointing_option(self):
        numericid = self.obs_settings.InstrumentPointingSolveOption()
        return instrument_pointing_lookup[numericid]

    @instrument_pointing_option.setter
    def instrument_pointing_option(self, val):
        if isinstance(val, (int, float)):
            val = instrument_pointing_lookup[val]

        val = self.obs_settings.stringToInstrumentPointingSolveOption(val)
        # This does not appear to be setting properly - the first arg needs to
        # be an InstrumentPositionSolveOptions
        self.obs_settings.setInstrumentPointingSettings(val, self.solve_for_twist)
        #self.settings.setObservationSolveOptions([self.obs_settings])

    @property
    def instrument_position_option(self):
        numericid = self.obs_settings.InstrumentPositionSolveOption()
        return instrument_position_lookup[numericid]

    @instrument_position_option.setter
    def instrument_position_option(self, val):
        if isinstance(val, (int, float)):
            val = instrument_position_lookup[val]

        val = self.obs_settings.stringToInstrumentPositionSolveOption(val)
        # This does not appear to be setting properly - the first arg needs to
        # be an InstrumentPositionSolveOptions
        self.obs_settings.setInstrumentPositionSettings(val, self.solve_for_twist)
        #self.settings.setObservationSolveOptions([self.obs_settings])

    def bundle(self, in_net, in_flist, print_summary=False):
        self.settings.setObservationSolveOptions([self.obs_settings])
        ba = bundle.Isis.BundleAdjust(self.settings, in_net, in_flist, print_summary)
        info = ba.solveCholeskyBR()
        results = info.bundleResults()

        control_points = results.bundleControlPoints()

        header = ['id', 'file_name', 'serial_num', 'focal_plane_measuredX(mm)',
                  'focal_plane_measuredY(mm)', 'sample', 'line', 'sample_residual',
                  'line_residual', 'residual_magnitude', 'is_rejected']
        data = []

        for point in control_points:
            measures = point.measures()
            for measure in measures:
                row = [
                    point.id(),
                    measure.parentBundleImage().fileName(),
                    measure.cubeSerialNumber(),
                    measure.focalPlaneMeasuredX(),
                    measure.focalPlaneMeasuredY(),
                    measure.sample(),
                    measure.line(),
                    measure.sampleResidual(),
                    measure.lineResidual(),
                    measure.residualMagnitude(),
                    measure.isRejected()]
                data.append(row)
        return results, pd.DataFrame(data, columns=header)

    def set_solve_options(self, settings):
        for k, v in settings.items():
            setattr(self, k, v)
            print(k, getattr(self, k))
