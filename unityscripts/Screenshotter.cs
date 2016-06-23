using UnityEngine;
using System.Collections;
using System.Collections.Generic;

public class Screenshotter : MonoBehaviour {
	public int resWidth = 448;
	public int resHeight = 448;
	public bool capture = true;
	public bool showBoundingBox = true;
	public bool skipImagesWithoutObjects = true;

	public string imagepath = "../unityshots/data/images/";
	public string labelpath = "../unityshots/data/labels/";

	public static bool backgroundNeedsUpdate = true;


	private ArrayList boundingBoxes = new ArrayList ();

	public GameObject[] cars;

	public RenderTexture rt;

	private static string ScreenShotName(int width, int height) {
		return string.Format("screen_{0}x{1}_{2}",
			width, height, 
			System.DateTime.Now.ToString("yyyy-MM-dd_HH-mm-ss.fff"));
	}

	void Start() {
		rt = new RenderTexture(resWidth, resHeight, 24);
		rt.antiAliasing = 8;
	}

	void LateUpdate(){
		boundingBoxes.Clear();

		if (showBoundingBox) {
			foreach (GameObject car in cars) {
				if (isVisible(car)) {
					boundingBoxes.Add (getBoundingBox (car));
				}
			}
		}

		if (capture) {
			captureScreen ();
		}
	}


	void OnGUI(){
		if (showBoundingBox) {
			foreach (Rect boundingBox in boundingBoxes) { 
				GUI.Box (boundingBox, "Object!");
			}
		}
	}

	void captureScreen() {
		string filename = ScreenShotName (resWidth, resHeight);
		string jpgfilename = imagepath + filename + ".jpg";
		string txtfilename = labelpath +filename + ".txt";


		GetComponent<Camera>().targetTexture = rt;
		GetComponent<Camera>().Render();
		RenderTexture.active = rt;

		if (dumpBoundingBoxes (txtfilename)) {
			Texture2D screenShot = new Texture2D(resWidth, resHeight, TextureFormat.RGB24, false);
			screenShot.ReadPixels(new Rect(0, 0, resWidth, resHeight), 0, 0);

			byte[] bytes = screenShot.EncodeToJPG (100);
			
			System.IO.File.WriteAllBytes(jpgfilename, bytes);
			Debug.Log(string.Format("Took screenshot to: {0}", filename));

			backgroundNeedsUpdate = true;
			Destroy (screenShot);
		}

		GetComponent<Camera>().targetTexture = null;
		RenderTexture.active = null;
	}

	bool dumpBoundingBoxes(string txtfilename){

		bool containsVisibleObjects = false;

		List<Rect> boxes = new List<Rect> ();

		Rect imageBounds = new Rect (0, 0, GetComponent<Camera> ().pixelWidth, GetComponent<Camera> ().pixelHeight);

		foreach (GameObject car in cars) {

			if (!isVisible (car)) {
				continue;
			}

			Rect bounds = getBoundingBox (car);

			float intersection = calculateIntersection (bounds, imageBounds);

			float percentageInside = intersection / calculateArea (bounds);

			if (percentageInside < 0.1 || bounds.width == 0 || bounds.height == 0) {
				Debug.Log (string.Format ("Visible box is too small: {0}", percentageInside));
				continue;
			}
			if (percentageInside >= 0.1 && percentageInside < 0.35) {
				containsVisibleObjects = false;
				break;
			}

			Debug.Log ("On screen");

			containsVisibleObjects = true;

			bounds = cropBoundingBoxToFit (bounds, imageBounds);

			boxes.Add (bounds);
		}

		string labels = "";

		for (int i = 0; i < boxes.Count; i++) {

			Rect bounds = boxes [i];
			float area = calculateArea (bounds);

			bool hasSignificantOverlap = false;
			for (int j = 0; j < boxes.Count; j++) {
				if (j == i) {
					continue;
				}
				float intersection = calculateIntersection (bounds, boxes [j]);
				if (intersection > 0.25 * area) {
					hasSignificantOverlap = true;
					break;
				}
			}

			if (hasSignificantOverlap) {
				containsVisibleObjects = false;
				break;
			}

			float x = bounds.center.x / imageBounds.width;
			float y = bounds.center.y / imageBounds.height;
			float w = bounds.width / imageBounds.width;
			float h = bounds.height / imageBounds.height;

			if (!labels.Equals ("")) {
				labels += "\n";
			}

			labels += "0 " + x + " " + y + " " + w + " " + h;
		}

		if (!containsVisibleObjects && skipImagesWithoutObjects) {
			Debug.Log (string.Format ("No objects in view"));
			return false;
		}
		System.IO.File.WriteAllText(txtfilename, labels);
		return true;
	}

	Rect getBoundingBox(GameObject gObject){

		MeshFilter myMeshFilter = gObject.GetComponent<MeshFilter> ();

		Bounds screenBounds = new Bounds();

		bool firstPass = true;

		//Iterate through my mesh.
		if (myMeshFilter != null) {
			Mesh myMesh = myMeshFilter.mesh;
			foreach (Vector3 vec in myMesh.vertices) {
				Vector3 worldSpacePoint = transform.TransformPoint (vec);
				Vector3 screenPoint = Camera.main.WorldToScreenPoint (worldSpacePoint);

				if (firstPass) {
					screenBounds = new Bounds (screenPoint, Vector3.zero); 
					firstPass = false;
				}

				screenBounds.Encapsulate (screenPoint);

			}
		}

		//Iterate through children meshes
		MeshFilter[] meshes = gObject.GetComponentsInChildren<MeshFilter>();
		foreach (MeshFilter meshfilt in meshes) {
			foreach (Vector3 vec in meshfilt.mesh.vertices) {
				Vector3 worldSpacePoint = meshfilt.transform.TransformPoint (vec);
				Vector3 screenPoint = Camera.main.WorldToScreenPoint (worldSpacePoint);

				if (firstPass) {
					screenBounds = new Bounds (screenPoint, Vector3.zero); 
					firstPass = false;
				}

				screenBounds.Encapsulate (screenPoint);

			}
		}

		Rect returnRect = new Rect ();

		int height = GetComponent<Camera> ().pixelHeight;
		returnRect.xMin = screenBounds.min.x;
		returnRect.yMin = height - screenBounds.max.y;
		returnRect.xMax = screenBounds.max.x;
		returnRect.yMax = height - screenBounds.min.y;

		return returnRect;

	}


	Rect cropBoundingBoxToFit(Rect boundingBox, Rect container) {
		if (boundingBox.xMax > container.xMax) {
			boundingBox.xMax = container.xMax;
		}

		if (boundingBox.xMin < container.xMin) {
			boundingBox.xMin = container.xMin;
		}

		if (boundingBox.yMax > container.yMax) {
			boundingBox.yMax = container.yMax;
		}

		if (boundingBox.yMin < container.yMin) {
			boundingBox.yMin = container.yMin;
		}
		return boundingBox;
	}


	bool isVisible(GameObject gObject){

		if (gObject.GetComponent<Renderer> () != null &&
			gObject.GetComponent<Renderer> ().isVisible) {
			return true;
		}
		foreach (Renderer render in gObject.GetComponentsInChildren<Renderer>()) {
			if (render.isVisible) {
				return true;
			}
		}
		return false;
	}

	float calculateIntersection(Rect a, Rect b) {
		float left = Mathf.Max (a.xMin, b.xMin);
		float right = Mathf.Min (a.xMax, b.xMax);
		float top = Mathf.Max (a.yMin, b.yMin);
		float bottom = Mathf.Min (a.yMax, b.yMax);

		if (left < right && top < bottom) {
			return (right - left) * (bottom - top);
		} else {
			return 0.0f;
		}
	}

	float calculateArea(Rect rectangle) {
		return rectangle.width * rectangle.height;
	}
}
