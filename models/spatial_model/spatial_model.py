import models.spatial_model.sm_config as sm_config


class SpatialModel:
    """Model integrates information relating to the physical environment"""

    def __is_point_in_rectangle(self, rect: sm_config.Rectangle, x: int, y: int):
        """Check if a point is inside a rectangle object
        :param rect: rectangle object
        :type rect: sm_config.Rectangle
        :param x: x position of the point
        :type x: int
        :param y: y position of the point
        :type y: int
        :return: True if the point is inside the rectangle, False otherwise
        :rtype: bool"""

        return rect.xmin <= x <= rect.xmax and rect.ymin <= y <= rect.ymax

    def __is_point_in_triangle(self, tri: sm_config.Triangle, x: int, y: int):
        """Check if a point is inside a triangle object using the barycentric method
        :param tri: triangle object
        :type tri: sm_config.Triangle
        :param x: x position of the point
        :type x: int
        :param y: y position of the point
        :type y: int
        :return: True if the point is inside the triangle, False otherwise
        :rtype: bool"""

        # Helper function to calculate the area of a triangle given its vertices
        def area(x1, y1, x2, y2, x3, y3) -> float:
            return abs((x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)) / 2.0)

        # Vertices of the triangle
        x1, y1 = tri.v1
        x2, y2 = tri.v2
        x3, y3 = tri.v3

        # Calculate the area of the full triangle
        a = area(x1, y1, x2, y2, x3, y3)

        # Calculate the area of the sub-triangles formed with the point (x, y)
        a1 = area(x, y, x2, y2, x3, y3)
        a2 = area(x1, y1, x, y, x3, y3)
        a3 = area(x1, y1, x2, y2, x, y)

        # The point is inside the triangle if the sum of a1, a2, and a3 equals the full area a
        return a == a1 + a2 + a3

    def __ensure_valid_grid_position(self, x_grid, y_grid):
        """Ensure the grid position is within the grid boundaries. Raise an error if the grid position is not valid
        :param x_grid: x position in grid points
        :type x_grid: int
        :param y_grid: y position in grid points
        :type y_grid: int"""

        is_valid = False  # Assume the grid position is not valid

        # check if the grid position is within (any of) the valid regions
        for valid_region in sm_config.VALID_REGIONS:
            if isinstance(valid_region, sm_config.Rectangle):
                if self.__is_point_in_rectangle(valid_region, x_grid, y_grid):
                    is_valid = True
                    break

            elif isinstance(valid_region, sm_config.Triangle):
                if self.__is_point_in_triangle(valid_region, x_grid, y_grid):
                    is_valid = True
                    break

        # Raise an error if the grid position is not safe
        if not is_valid:
            raise ValueError(
                f"Grid position ({x_grid}, {y_grid}) is not within any valid region"
            )

    def compute_spatial_pose(
        self,
        x_g: int,
        y_g: int,
        table_distance: float = 0,
        perform_safety_check: bool = False,
    ):
        """Compute the x, y, z position of the robot based on the grid position
        :param x_g: x position in grid points
        :type x_g: int
        :param y_g: y position in grid points
        :type y_g: int
        :param table_distance: distance from the table in meters
        :type table_distance: float
        :param perform_safety_check: flag to perform safety check on the grid position
        :type perform_safety_check: bool
        :return: spatial pose (x, y, z, roll, pitch, yaw) of the robot
        :rtype: list
        """

        # Ensure the grid position is within the grid boundaries
        if perform_safety_check:
            self.__ensure_valid_grid_position(x_g, y_g)

        # Calculate base values
        comp_x = sm_config.X_BASE_MIN + x_g * sm_config.HOLE_DIST
        comp_y = sm_config.Y_BASE_MIN + y_g * sm_config.HOLE_DIST

        # comp_z = sm_config.Z_BASE_MIN + z_g * sm_config.HOLE_DIST
        comp_z = sm_config.Z_BASE_MIN + table_distance

        # return position as list
        return [comp_x, comp_y, comp_z, sm_config.YAW, sm_config.PITCH, sm_config.ROLL]
