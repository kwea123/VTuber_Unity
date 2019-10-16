using UnityEngine;
using System.Collections;

using System;
using System.Threading;
using System.Net;
using System.Net.Sockets;
using System.Text;

namespace UnityChan
{
    [RequireComponent(typeof(Animator))]

    public class UnityChanControlScriptWithRgidBody : MonoBehaviour
    {

        public float eye_close, eye_open, mouth_close, mouth_open;

        private Animator anim;

        private float roll=0, pitch=0, yaw=0, min_ear=1.0f, mar=0f, mdst=0.25f;

        // Thread
        Thread receiveThread;
        TcpClient client;
        TcpListener listener;
        int port = 5066;


        public SkinnedMeshRenderer eye, eye_lid, mouth, eyebrow;
        private Transform neck;
        private Quaternion neck_quat;

        // 初期化
        void Start ()
        {
            Application.targetFrameRate = 30;
            anim = GetComponent<Animator> ();

            neck = anim.GetBoneTransform (HumanBodyBones.Neck);
            neck_quat = Quaternion.Euler(0, -90, -90);

            InitTCP();

            // for (int index = 0; index < eyebrow.sharedMesh.blendShapeCount; index++){
            //     print(eyebrow.sharedMesh.GetBlendShapeName(index));
            // }
        }

        private void InitTCP()
        {
            receiveThread = new Thread (new ThreadStart(ReceiveData));
            receiveThread.IsBackground = true;
            receiveThread.Start();
        }

        private void ReceiveData()
        {
            try {           
                listener = new TcpListener(IPAddress.Parse("127.0.0.1"), port);
                listener.Start();
                Byte[] bytes = new Byte[1024];
                while (true) {
                    using (client = listener.AcceptTcpClient()) {
                        using (NetworkStream stream = client.GetStream()) {
                            int length;
                            while ((length = stream.Read(bytes, 0, bytes.Length)) != 0) {
                                var incommingData = new byte[length];
                                Array.Copy(bytes, 0, incommingData, 0, length);
                                string clientMessage = Encoding.ASCII.GetString(incommingData);
                                string[] res = clientMessage.Split(' ');
                                roll = float.Parse(res[0])*0.4f + roll*0.6f;
                                pitch = float.Parse(res[1])*0.4f + pitch*0.6f;
                                yaw = float.Parse(res[2])*0.4f + yaw*0.6f;
                                min_ear = float.Parse(res[3]);
                                mar = float.Parse(res[4])*0.4f + mar*0.6f;
                                mdst = float.Parse(res[5]);
                            }
                        }
                    }
                }
            } catch(Exception e) {
                print (e.ToString());
            }
        }
    
        void OnAnimatorIK (int layerIndex)
        {
            
            // Vector3 lookPos = Quaternion.Euler(pitch, yaw, roll) * (Camera.main.transform.position-head)+head;
            // anim.SetLookAtWeight(1.0f, 0.0f, 1.0f, 1.0f, 0.5f);
            // anim.SetLookAtPosition(lookPos);
            // print(lookPos);
        }


        void Update() 
        {

            // set paramters

            min_ear = Mathf.Clamp(min_ear, eye_close, eye_open);
            float eyeratio = -100/(eye_open-eye_close)*(min_ear-eye_open);
            
            mar = Mathf.Clamp(mar, mouth_close, mouth_open);
            float mouthratio = 100/(mouth_open-mouth_close)*(mar-mouth_close);
            
            // do rotation, etc.
            neck.rotation = Quaternion.Euler(-pitch, yaw, -roll) * neck_quat;
            if (mdst > 0.33f){
                anim.SetLayerWeight(1, 1f);
                anim.CrossFade ("smile1@unitychan", 0.1f);
            } else {
                anim.SetLayerWeight(1, 1f);
                anim.CrossFade ("default@unitychan", 0.1f);
                // eye.SetBlendShapeWeight (6, eyeratio);
                // eye_lid.SetBlendShapeWeight (6, eyeratio);

                if (mouthratio > 70){
                    eye.SetBlendShapeWeight (2, 100);
                    eyebrow.SetBlendShapeWeight (2, 100);
                    mouth.SetBlendShapeWeight (0, mouthratio);
                } else {
                    mouth.SetBlendShapeWeight (2, mouthratio);
                    mouth.SetBlendShapeWeight (1, 80);
                }
            }
            
        }

        void LateUpdate()
        {
            
        }

        void OnApplicationQuit()
        {
            try
            {
                client.Close();
            }
            catch(Exception e)
            {
                Debug.Log(e.Message);
            }

            try
            {
                listener.Stop();
            }
            catch(Exception e)
            {
                Debug.Log(e.Message);
            }
        }
    
        // 以下、メイン処理.リジッドボディと絡めるので、FixedUpdate内で処理を行う.
        // void FixedUpdate ()
        // {

        //  float h = Input.GetAxis ("Horizontal");             // 入力デバイスの水平軸をhで定義
        //  float v = Input.GetAxis ("Vertical");               // 入力デバイスの垂直軸をvで定義
        //  anim.SetFloat ("Speed", v);                         // Animator側で設定している"Speed"パラメタにvを渡す
        //  anim.SetFloat ("Direction", h);                         // Animator側で設定している"Direction"パラメタにhを渡す
        //  anim.speed = animSpeed;                             // Animatorのモーション再生速度に animSpeedを設定する
        //  currentBaseState = anim.GetCurrentAnimatorStateInfo (0);    // 参照用のステート変数にBase Layer (0)の現在のステートを設定する
        //  rb.useGravity = true;//ジャンプ中に重力を切るので、それ以外は重力の影響を受けるようにする
        
        
        
        //  // 以下、キャラクターの移動処理
        //  velocity = new Vector3 (0, 0, v);       // 上下のキー入力からZ軸方向の移動量を取得
        //  // キャラクターのローカル空間での方向に変換
        //  velocity = transform.TransformDirection (velocity);
        //  //以下のvの閾値は、Mecanim側のトランジションと一緒に調整する
        //  if (v > 0.1) {
        //      velocity *= forwardSpeed;       // 移動速度を掛ける
        //  } else if (v < -0.1) {
        //      velocity *= backwardSpeed;  // 移動速度を掛ける
        //  }
        
        //  if (Input.GetButtonDown ("Jump")) { // スペースキーを入力したら

        //      //アニメーションのステートがLocomotionの最中のみジャンプできる
        //      if (currentBaseState.nameHash == locoState) {
        //          //ステート遷移中でなかったらジャンプできる
        //          if (!anim.IsInTransition (0)) {
        //              rb.AddForce (Vector3.up * jumpPower, ForceMode.VelocityChange);
        //              anim.SetBool ("Jump", true);        // Animatorにジャンプに切り替えるフラグを送る
        //          }
        //      }
        //  }
        

        //  // 上下のキー入力でキャラクターを移動させる
        //  transform.localPosition += velocity * Time.fixedDeltaTime;

        //  // 左右のキー入力でキャラクタをY軸で旋回させる
        //  transform.Rotate (0, h * rotateSpeed, 0);   
    

        //  // 以下、Animatorの各ステート中での処理
        //  // Locomotion中
        //  // 現在のベースレイヤーがlocoStateの時
        //  if (currentBaseState.nameHash == locoState) {
        //      //カーブでコライダ調整をしている時は、念のためにリセットする
        //      if (useCurves) {
        //          resetCollider ();
        //      }
        //  }
        // // JUMP中の処理
        // // 現在のベースレイヤーがjumpStateの時
        // else if (currentBaseState.nameHash == jumpState) {
        //      cameraObject.SendMessage ("setCameraPositionJumpView"); // ジャンプ中のカメラに変更
        //      // ステートがトランジション中でない場合
        //      if (!anim.IsInTransition (0)) {
                
        //          // 以下、カーブ調整をする場合の処理
        //          if (useCurves) {
        //              // 以下JUMP00アニメーションについているカーブJumpHeightとGravityControl
        //              // JumpHeight:JUMP00でのジャンプの高さ（0〜1）
        //              // GravityControl:1⇒ジャンプ中（重力無効）、0⇒重力有効
        //              float jumpHeight = anim.GetFloat ("JumpHeight");
        //              float gravityControl = anim.GetFloat ("GravityControl"); 
        //              if (gravityControl > 0)
        //                  rb.useGravity = false;  //ジャンプ中の重力の影響を切る
                                        
        //              // レイキャストをキャラクターのセンターから落とす
        //              Ray ray = new Ray (transform.position + Vector3.up, -Vector3.up);
        //              RaycastHit hitInfo = new RaycastHit ();
        //              // 高さが useCurvesHeight 以上ある時のみ、コライダーの高さと中心をJUMP00アニメーションについているカーブで調整する
        //              if (Physics.Raycast (ray, out hitInfo)) {
        //                  if (hitInfo.distance > useCurvesHeight) {
        //                      col.height = orgColHight - jumpHeight;          // 調整されたコライダーの高さ
        //                      float adjCenterY = orgVectColCenter.y + jumpHeight;
        //                      col.center = new Vector3 (0, adjCenterY, 0);    // 調整されたコライダーのセンター
        //                  } else {
        //                      // 閾値よりも低い時には初期値に戻す（念のため）                   
        //                      resetCollider ();
        //                  }
        //              }
        //          }
        //          // Jump bool値をリセットする（ループしないようにする）               
        //          anim.SetBool ("Jump", false);
        //      }
        //  }
        // // IDLE中の処理
        // // 現在のベースレイヤーがidleStateの時
        // else if (currentBaseState.nameHash == idleState) {
        //      //カーブでコライダ調整をしている時は、念のためにリセットする
        //      if (useCurves) {
        //          resetCollider ();
        //      }
        //      // スペースキーを入力したらRest状態になる
        //      if (Input.GetButtonDown ("Jump")) {
        //          anim.SetBool ("Rest", true);
        //      }
        //  }
        // // REST中の処理
        // // 現在のベースレイヤーがrestStateの時
        // else if (currentBaseState.nameHash == restState) {
        //      //cameraObject.SendMessage("setCameraPositionFrontView");       // カメラを正面に切り替える
        //      // ステートが遷移中でない場合、Rest bool値をリセットする（ループしないようにする）
        //      if (!anim.IsInTransition (0)) {
        //          anim.SetBool ("Rest", false);
        //      }
        //  }
        // }

        // void OnGUI ()
        // {
        //     GUI.Box (new Rect (Screen.width - 260, 10, 250, 150), "Interaction");
        //     GUI.Label (new Rect (Screen.width - 245, 30, 250, 30), "Up/Down Arrow : Go Forwald/Go Back");
        //     GUI.Label (new Rect (Screen.width - 245, 50, 250, 30), "Left/Right Arrow : Turn Left/Turn Right");
        //     GUI.Label (new Rect (Screen.width - 245, 70, 250, 30), "Hit Space key while Running : Jump");
        //     GUI.Label (new Rect (Screen.width - 245, 90, 250, 30), "Hit Spase key while Stopping : Rest");
        //     GUI.Label (new Rect (Screen.width - 245, 110, 250, 30), "Left Control : Front Camera");
        //     GUI.Label (new Rect (Screen.width - 245, 130, 250, 30), "Alt : LookAt Camera");
        // }


    }
}
